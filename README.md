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
Tracing block device I/O... Hit Ctrl-C to end.

lee@ubuntu:~$ sudo python io.py
09:04:38
IO count : 37  //IO数量
(us) :	<64(2%)	<256(8%)	<512(10%)	<32768(54%)	<65536(100%)	//IO延迟统计：2%的IO延迟低于64us，8%的IO延迟低于256us，依次类推...
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

09:04:44
IO count : 1
(us) :	<128(100%)	
     latency(us)         : count     distribution
         0 -> 1          : 0        |                                        |
         2 -> 3          : 0        |                                        |
         4 -> 7          : 0        |                                        |
         8 -> 15         : 0        |                                        |
        16 -> 31         : 0        |                                        |
        32 -> 63         : 0        |                                        |
        64 -> 127        : 1        |****************************************|

09:04:47
IO count : 4
(us) :	<64(25%)	<128(50%)	<512(75%)	<16384(100%)	
     latency(us)         : count     distribution
         0 -> 1          : 0        |                                        |
         2 -> 3          : 0        |                                        |
         4 -> 7          : 0        |                                        |
         8 -> 15         : 0        |                                        |
        16 -> 31         : 0        |                                        |
        32 -> 63         : 1        |****************************************|
        64 -> 127        : 1        |****************************************|
       128 -> 255        : 0        |                                        |
       256 -> 511        : 1        |****************************************|
       512 -> 1023       : 0        |                                        |
      1024 -> 2047       : 0        |                                        |
      2048 -> 4095       : 0        |                                        |
      4096 -> 8191       : 0        |                                        |
      8192 -> 16383      : 1        |****************************************|

09:04:50
IO count : 48
(us) :	<64(2%)	<512(10%)	<1024(66%)	<2048(85%)	<16384(87%)	<32768(89%)	<65536(93%)	<131072(100%)	
     latency(us)         : count     distribution
         0 -> 1          : 0        |                                        |
         2 -> 3          : 0        |                                        |
         4 -> 7          : 0        |                                        |
         8 -> 15         : 0        |                                        |
        16 -> 31         : 0        |                                        |
        32 -> 63         : 1        |*                                       |
        64 -> 127        : 0        |                                        |
       128 -> 255        : 0        |                                        |
       256 -> 511        : 4        |*****                                   |
       512 -> 1023       : 27       |****************************************|
      1024 -> 2047       : 9        |*************                           |
      2048 -> 4095       : 0        |                                        |
      4096 -> 8191       : 0        |                                        |
      8192 -> 16383      : 1        |*                                       |
     16384 -> 32767      : 1        |*                                       |
     32768 -> 65535      : 2        |**                                      |
     65536 -> 131071     : 3        |****                                    |
     
 参考：
 ebpf/bcc https://www.iovisor.org/technology/ebpf
 ebpf_exporter更加人性化显示 https://github.com/cloudflare/ebpf_exporter
