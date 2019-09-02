topio

Q：考虑“当系统脏页比例到达 dirty_ratio 后，对每个执行 IO 请求的线程带来的延迟影响是怎样的”
A：（当脏页占系统内存的比例超过/proc/sys/vm/dirty_background_ratio 的时候，write系统调用会唤醒pdflush回写脏页,直到脏页比例低于
/proc/sys/vm/dirty_background_ratio，但write系统调用不会被阻塞，立即返回）
若脏页比例超过 dirty_ratio （/proc/sys/vm/dirty_ratio）后，系统主动回写脏页，且write被阻塞，直到脏页比例低于dirty_ratio.

该程序使用eBPFF/bcc工具，持续监测io延迟。
用法类似于top指令，如-n表示显示次数，-d刷新显示的间隔。示例如下：

lee@ubuntu:~$ sudo python io.py -h
usage: io.py [-h] [-D] [-Q] [-F] [-m] [-u] [-d] [-n]

Summarize block device I/O latency as a histogram

optional arguments:
  -h, --help          show this help message and exit
  -D, --disks         print a histogram per disk device
  -Q, --queued        include OS queued time in I/O time
  -F, --flags         print a histogram per set of I/O flags
  -m, --milliseconds  millisecond(ms) histogram
  -u, --microseconds  microsecond(us) histogram
  -d, --interval      output interval, in seconds
  -n, --count         number of outputs

examples:
    ./topio            # = topio -d 3
    ./topio -m         # 时间单位ms
    ./topio -u         # 时间单位us
    ./topio -n 1       # 显示一次
    ./topio -d 3       # 每隔3秒刷新一次
    ./topio -Q         # include OS queued time in I/O time
    ./topio -D         # show each disk device separately
    ./topio -F         # show I/O flags separately
Tracing block device I/O... Hit Ctrl-C to end.

lee@ubuntu:~$ sudo python io.py
09:04:38
IO count : 37 //含义：IO数量37
(us) :	<64(2%)	<256(8%)	<512(10%)	<32768(54%)	<65536(100%)	//含义：2%的IO延迟低于64us，8%的IO延迟低于256us，依次类推...
     latency(us)         : count     distribution
         0 -> 1          : 0        |                                        |
         2 -> 3          : 0        |                                        |
         4 -> 7          : 0        |                                        |
         8 -> 15         : 0        |                                        |
        16 -> 31         : 0        |                                        |
        32 -> 63         : 1        |**                                      |
        64 -> 127        : 0        |                                        |
       128 -> 255        : 2        |****                                    |
       256 -> 511        : 1        |**                                      |
       512 -> 1023       : 0        |                                        |
      1024 -> 2047       : 0        |                                        |
      2048 -> 4095       : 0        |                                        |
      4096 -> 8191       : 0        |                                        |
      8192 -> 16383      : 0        |                                        |
     16384 -> 32767      : 16       |*************************************   |
     32768 -> 65535      : 17       |****************************************|

09:04:41
IO count : 5
(us) :	<64(20%)	<256(40%)	<512(60%)	<16384(80%)	<32768(100%)	
     latency(us)         : count     distribution
         0 -> 1          : 0        |                                        |
         2 -> 3          : 0        |                                        |
         4 -> 7          : 0        |                                        |
         8 -> 15         : 0        |                                        |
        16 -> 31         : 0        |                                        |
        32 -> 63         : 1        |****************************************|
        64 -> 127        : 0        |                                        |
       128 -> 255        : 1        |****************************************|
       256 -> 511        : 1        |****************************************|
       512 -> 1023       : 0        |                                        |
      1024 -> 2047       : 0        |                                        |
      2048 -> 4095       : 0        |                                        |
      4096 -> 8191       : 0        |                                        |
      8192 -> 16383      : 1        |****************************************|
     16384 -> 32767      : 1        |****************************************|
 
解释:
每隔-d秒刷新一次；
IO count : 37  // IO数量
(us) :	<64(2%)	<256(8%)	<512(10%)	<32768(54%)	<65536(100%)	//IO延迟统计：2%的IO延迟低于64us，8%的IO延迟低于256us，依次类推...


上面仅是控制台显示，可用ebpf_exporter使显示更人性化图形化
（可惜，弄了半天，一直报错“ Error attaching exporter: failed to attach to program "topio": failed to attach kprobes:
failed to attach probe "blk_start_request" to "trace_req_start": failed to attach BPF kprobe: no such file or directory”，
还没fix）

 参考：
 ebpf/bcc https://www.iovisor.org/technology/ebpf
 ebpf_exporter显示 https://github.com/cloudflare/ebpf_exporter
