
# check number of drop packets in trace file
drop_packets = 0;
throughput = 0;
throughput_packets = 0;
start_time = 0;
end_time = 0;
with open('exp1.tr') as fp:
    for line in fp:
        words = line.split()
        if line[0] is 'd' and words[4] == 'tcp':
            drop_packets = drop_packets + 1
        if line[0] is 'r':
            if (words[3] == '4' and words[4] == 'tcp') or (words[3] == '0' and words[4] == 'ack'):
                if start_time == 0:
                    start_time = float(words[1])
                end_time = float(words[1])   
                throughput = throughput + int(words[5])
                throughput_packets = throughput_packets + 1

time = (end_time - start_time)
print ('start : ' + str(start_time))
print ('end : ' + str(end_time))
# packets in MB
throughput = (8*throughput) / (1024*1024)

print ('Total packets received : ' + str(throughput_packets))

f = open('result.txt', 'a')
f.write('drop_packets : ' + str(drop_packets) + '\n')
f.write('throughput : ' + str(format(throughput/time, '.3f')) + ' Mbps' +'\n')
f.write('latency : ' + str(format((1000*time)/throughput_packets, '.3f')) + ' ms' + '\n' + '\n')
f.close()

