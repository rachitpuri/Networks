f = open('results3.txt', 'a')

throughput_tcp = 0;
throughput_cbr = 0;
start_time = 0;
end_time = 0;
tcp_throughput_packets = 0;
cbr_throughput_packets = 0;
interval = 1;
base = 0;
with open('exp3.tr') as fp:
    for line in fp:
        if line[0] is 'r':
            words = line.split()
            if (words[3] == '4' and words[4] == 'tcp') or (words[3] == '5' and words[4] == 'cbr') or (words[3] == '0' and words[4] == 'ack'):
                if start_time == 0:
                    start_time = float(words[1])
                end_time = float(words[1])
                if end_time > (base + interval):
                    f.write('Interval : ' + str(format(start_time, '.1f')) + ' - ' + str(format(end_time, '.1f')) + '\n')
                    time = (end_time - start_time)
                    print ('time : ' + str(time))
                    # packets in MB
                    throughput_tcp = (8*throughput_tcp) / 1024
                    throughput_cbr = (8*throughput_cbr) / 1024
                    f.write('TCP packets : ' +str(tcp_throughput_packets) + '\n')
                    f.write('TCP throughput : ' + str(format(throughput_tcp/1.0, '.3f')) + '\n')
                    f.write('TCP latency : ' + str(format((1000*1.0)/tcp_throughput_packets, '.3f')) + ' ms' + '\n' + '\n')                    
                    if cbr_throughput_packets > 0:
                        f.write('CBR packets : ' +str(cbr_throughput_packets) + '\n')
			f.write('CBR throughput : ' + str(format(throughput_cbr/1.0, '.3f')) + '\n')
                        f.write('CBR latency : ' + str(format((1000*1.0)/cbr_throughput_packets, '.3f')) + ' ms' + '\n' + '\n')
                    else:
                        f.write('CBR throughput : ' + '0' + '\n')
                        f.write('CBR latency : ' + '0 ms' + '\n' + '\n')
                    base = base + interval
                    tcp_throughput_packets = 0
                    cbr_throughput_packets = 0
                    throughput_tcp = 0
                    throughput_cbr = 0
                    start_time = end_time
                else:
                    if words[4] == 'tcp' or words[4] == 'ack':   
                        tcp_throughput_packets = tcp_throughput_packets + 1
                        throughput_tcp = throughput_tcp + int(words[5])
                    else:
                        cbr_throughput_packets = cbr_throughput_packets + 1
                        throughput_cbr = throughput_cbr + int(words[5])

f.write('Interval : ' + '19.0 - 20.0' + '\n')
# packets in MB
throughput_tcp = (8*throughput_tcp) / 1024
throughput_cbr = (8*throughput_cbr) / 1024
f.write('TCP packets : ' +str(tcp_throughput_packets) + '\n')
f.write('TCP throughput : ' + str(format(throughput_tcp/1.0, '.3f')) + '\n')
f.write('TCP latency : ' + str(format((1000*1.0)/tcp_throughput_packets, '.3f')) + ' ms' + '\n')
f.write('CBR throughput : ' + str(format(throughput_cbr/1.0, '.3f')) + '\n')
f.write('CBR latency : ' + str(format((1000*1.0)/cbr_throughput_packets, '.3f')) + ' ms' + '\n' + '\n')

f.close()

