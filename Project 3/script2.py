
# check number of drop packets in trace file
drop_packets = 0;
throughput_link1 = 0;
throughput_packets_link1 = 0;
throughput_link2 = 0;
throughput_packets_link2 = 0;
start_time_link1 = 0;
end_time_link1 = 0;
start_time_link2 = 0;
end_time_link2 = 0;

with open('exp2.tr') as fp:
    for line in fp:
        words = line.split()
        if line[0] is 'd' and words[4] == 'tcp':
            drop_packets = drop_packets + 1
        if line[0] is 'r':
            if (words[3] == '4' and words[4] == 'tcp') or (words[3] == '0' and words[4] == 'ack'):
                if start_time_link1 == 0:
                    start_time_link1 = float(words[1])
                end_time_link1 = float(words[1])   
                throughput_link1 = throughput_link1 + int(words[5])
                throughput_packets_link1 = throughput_packets_link1 + 1
            if (words[3] == '5' and words[4] == 'tcp') or (words[3] == '1' and words[4] == 'ack'):
                if start_time_link2 == 0:
                    start_time_link2 = float(words[1])
                end_time_link2 = float(words[1])   
                throughput_link2 = throughput_link2 + int(words[5])
                throughput_packets_link2 = throughput_packets_link2 + 1

time_link1 = (end_time_link1 - start_time_link1)
time_link2 = (end_time_link2 - start_time_link2)
# packets in MB
throughput_link1 = (8*throughput_link1) / (1024*1024)
throughput_link2 = (8*throughput_link2) / (1024*1024)

f = open('result2.txt', 'a')
f.write('Link1' + '\n')
f.write('drop_packets : ' + str(drop_packets) + '\n')
f.write('throughput : ' + str(format(throughput_link1/time_link1, '.3f')) + ' Mbps' + '\n')
f.write('latency : ' + str(format((1000*time_link1)/throughput_packets_link1, '.3f')) + ' ms' + '\n' + '\n')
f.write('Link2' + '\n')
f.write('drop_packets : ' + str(drop_packets) + '\n')
f.write('throughput : ' + str(format(throughput_link2/time_link2, '.3f')) + ' Mbps' '\n')
f.write('latency : ' + str(format((1000*time_link2)/throughput_packets_link2, '.3f')) + ' ms' + '\n' + '\n')
f.close()

