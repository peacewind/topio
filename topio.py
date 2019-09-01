#!/usr/bin/python
# -*- coding:utf-8 -*-
# 统计系统IO延迟
from __future__ import print_function
from bcc import BPF
from time import sleep, strftime
import argparse

# arguments
examples = """examples:
    ./topio            # = topio -d 3
    ./topio -m         # 时间单位ms
    ./topio -u         # 时间单位us
    ./topio -n 1       # 显示一次
    ./topio -d 3       # 每隔3秒刷新一次
    ./topio -Q         # include OS queued time in I/O time
    ./topio -D         # show each disk device separately
    ./topio -F         # show I/O flags separately
"""
parser = argparse.ArgumentParser(
    description="Summarize block device I/O latency as a histogram",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog=examples)
parser.add_argument("-D", "--disks", action="store_true", help="print a histogram per disk device")
parser.add_argument("-Q", "--queued", action="store_true", help="include OS queued time in I/O time")
parser.add_argument("-F", "--flags", action="store_true", help="print a histogram per set of I/O flags")
parser.add_argument("-m", "--milliseconds", action="store_true", help="millisecond(ms) histogram")
parser.add_argument("-u", "--microseconds", action="store_true", help="microsecond(us) histogram")
parser.add_argument("-d", "--interval", action="store_true", help="output interval, in seconds", default=3)
parser.add_argument("-n", "--count", action="store_true", help="number of outputs", default=99999999)
parser.add_argument("--ebpf", action="store_true", help=argparse.SUPPRESS)
args = parser.parse_args()
countdown = int(args.count)
debug = 0
if args.flags and args.disks:
    print("ERROR: can only use -D or -F. Exiting.")
    exit()

# define BPF program
bpf_text = """
#include <uapi/linux/ptrace.h>
#include <linux/blkdev.h>

typedef struct disk_key {
    char disk[DISK_NAME_LEN];
    u64 slot;
} disk_key_t;

typedef struct flag_key {
    u64 flags;
    u64 slot;
} flag_key_t;

BPF_HASH(start, struct request *);
STORAGE

// time block I/O
int trace_req_start(struct pt_regs *ctx, struct request *req)
{
    u64 ts = bpf_ktime_get_ns();
    start.update(&req, &ts);
    return 0;
}

// output
int trace_req_done(struct pt_regs *ctx, struct request *req)
{
    u64 *tsp, delta;

    // fetch timestamp and calculate delta
    tsp = start.lookup(&req);
    if (tsp == 0) {
        return 0;   // missed issue
    }
    delta = bpf_ktime_get_ns() - *tsp;
    FACTOR

    // store as histogram
    STORE

    start.delete(&req);
    return 0;
}
"""

# code substitutions
if args.milliseconds:
    bpf_text = bpf_text.replace('FACTOR', 'delta /= 1000000;')
    label = "latency(ms)"
else:  # elif args.microseconds
    bpf_text = bpf_text.replace('FACTOR', 'delta /= 1000;')
    label = "latency(us)"
if args.disks:
    bpf_text = bpf_text.replace('STORAGE', 'BPF_HISTOGRAM(dist, disk_key_t);')
    bpf_text = bpf_text.replace('STORE', 'disk_key_t key = {.slot = bpf_log2l(delta)}; ' +
                                'void *__tmp = (void *)req->rq_disk->disk_name; ' +
                                'bpf_probe_read(&key.disk, sizeof(key.disk), __tmp); ' +
                                'dist.increment(key);')
elif args.flags:
    bpf_text = bpf_text.replace('STORAGE', 'BPF_HISTOGRAM(dist, flag_key_t);')
    bpf_text = bpf_text.replace('STORE', 'flag_key_t key = {.slot = bpf_log2l(delta)}; ' +
                                'key.flags = req->cmd_flags; ' + 'dist.increment(key);')
else:
    bpf_text = bpf_text.replace('STORAGE', 'BPF_HISTOGRAM(dist);')
    bpf_text = bpf_text.replace('STORE', 'dist.increment(bpf_log2l(delta));')
if debug or args.ebpf:
    print(bpf_text)
    if args.ebpf:
        exit()

# load BPF program
b = BPF(text=bpf_text)
if args.queued:
    b.attach_kprobe(event="blk_account_io_start", fn_name="trace_req_start")
else:
    if BPF.get_kprobe_functions(b'blk_start_request'):
        b.attach_kprobe(event="blk_start_request", fn_name="trace_req_start")
    b.attach_kprobe(event="blk_mq_start_request", fn_name="trace_req_start")
b.attach_kprobe(event="blk_account_io_done", fn_name="trace_req_done")

print("Tracing block device I/O... Hit Ctrl-C to end.")

# see blk_fill_rwbs():
req_opf = {
    0: "Read",
    1: "Write",
    2: "Flush",
    3: "Discard",
    5: "SecureErase",
    6: "ZoneReset",
    7: "WriteSame",
    9: "WriteZeros"
}
REQ_OP_BITS = 8
REQ_OP_MASK = ((1 << REQ_OP_BITS) - 1)
REQ_SYNC = 1 << (REQ_OP_BITS + 3)
REQ_META = 1 << (REQ_OP_BITS + 4)
REQ_PRIO = 1 << (REQ_OP_BITS + 5)
REQ_NOMERGE = 1 << (REQ_OP_BITS + 6)
REQ_IDLE = 1 << (REQ_OP_BITS + 7)
REQ_FUA = 1 << (REQ_OP_BITS + 9)
REQ_RAHEAD = 1 << (REQ_OP_BITS + 11)
REQ_BACKGROUND = 1 << (REQ_OP_BITS + 12)
REQ_NOWAIT = 1 << (REQ_OP_BITS + 13)


def flags_print(flags):
    desc = ""
    # operation
    if flags & REQ_OP_MASK in req_opf:
        desc = req_opf[flags & REQ_OP_MASK]
    else:
        desc = "Unknown"
    # flags
    if flags & REQ_SYNC:
        desc = "Sync-" + desc
    if flags & REQ_META:
        desc = "Metadata-" + desc
    if flags & REQ_FUA:
        desc = "ForcedUnitAccess-" + desc
    if flags & REQ_PRIO:
        desc = "Priority-" + desc
    if flags & REQ_NOMERGE:
        desc = "NoMerge-" + desc
    if flags & REQ_IDLE:
        desc = "Idle-" + desc
    if flags & REQ_RAHEAD:
        desc = "ReadAhead-" + desc
    if flags & REQ_BACKGROUND:
        desc = "Background-" + desc
    if flags & REQ_NOWAIT:
        desc = "NoWait-" + desc
    return desc


# def printSumary()

# output
exiting = 0
dist = b.get_table("dist")

while (1):
    try:
        sleep(int(args.interval))
    except KeyboardInterrupt:
        exiting = 1

    print("\n%-8s\n" % strftime("%H:%M:%S"), end="")

    # print('\033c',end='')
    latency_list = []
    total = 0
    for k, v in dist.items():
        if v.value > 0:
            latency_list.append((k.value - 1, v.value))
            total += v.value
    latency_list.sort()
    currnum = long(0)
    print("IO count :", total)
    print(label[-4:], ":\t", end="")
    for k, v in latency_list:
        currnum += v
        print("<", 2 << k, "(", int(100 * currnum / total), "%)\t", end="", sep="")
    print()
    if args.flags:
        dist.print_log2_hist(label, "flags", flags_print)
    else:
        dist.print_log2_hist(label, "disk")

    dist.clear()

    countdown -= 1
    if exiting or countdown == 0:
        exit()
