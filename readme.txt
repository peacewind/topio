# topio
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

 参考：
 ebpf/bcc https://www.iovisor.org/technology/ebpf
 ebpf_exporter更加人性化显示 https://github.com/cloudflare/ebpf_exporter
