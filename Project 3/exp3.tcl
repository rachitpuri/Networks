 # Create a ns object
set ns [new Simulator]
$ns color 1 Blue
$ns color 2 Red

# Open the Trace files
set TraceFile [open exp3.tr w]
$ns trace-all $TraceFile

set version [lindex $argv 0]
set q_algo [lindex $argv 1] 

proc finish {} {
	global ns TraceFile
	$ns flush-trace
	close $TraceFile
	#exec nam outtcp3.nam &
	exit 0
}

# Create six nodes
set n0 [$ns node]
set n1 [$ns node]
set n2 [$ns node]
set n3 [$ns node]
set n4 [$ns node]
set n5 [$ns node]

#create links between the nodes
if {$q_algo eq "DropTail"} {
$ns duplex-link $n0 $n2 6Mb 10ms DropTail
$ns duplex-link $n1 $n2 6Mb 10ms DropTail
$ns duplex-link $n2 $n3 6Mb 10ms DropTail
$ns duplex-link $n3 $n4 6Mb 10ms DropTail
$ns duplex-link $n3 $n5 6Mb 10ms DropTail
} elseif {$q_algo eq "RED"} {
$ns duplex-link $n0 $n2 6Mb 10ms RED
$ns duplex-link $n1 $n2 6Mb 10ms RED
$ns duplex-link $n2 $n3 6Mb 10ms RED
$ns duplex-link $n3 $n4 6Mb 10ms RED
$ns duplex-link $n3 $n5 6Mb 10ms RED
}

#set queue size
$ns queue-limit $n0 $n2 10
$ns queue-limit $n1 $n2 10
$ns queue-limit $n2 $n3 10
$ns queue-limit $n3 $n4 10
$ns queue-limit $n3 $n5 10

$ns duplex-link-op $n0 $n2 orient right-down
$ns duplex-link-op $n1 $n2 orient right-up
$ns duplex-link-op $n2 $n3 orient right
$ns duplex-link-op $n3 $n4 orient right-up
$ns duplex-link-op $n3 $n5 orient right-down


#Setup a UDP connection
set udp0 [new Agent/UDP]
$ns attach-agent $n1 $udp0
set null0 [new Agent/Null]
$ns attach-agent $n5 $null0
$ns connect $udp0 $null0

#Setup a CBR over UDP connection
set cbr0 [new Application/Traffic/CBR]
$cbr0 attach-agent $udp0
$cbr0 set type_ CBR
$cbr0 set rate_ 5mb

#Setup a TCP conncection
if {$version eq "Reno"} {
set tcp1 [new Agent/TCP/Reno]
set sink1 [new Agent/TCPSink]
} elseif {$version eq "SACK"} {
set tcp1 [new Agent/TCP/Sack1]
set sink1 [new Agent/TCPSink/Sack1]
}

$tcp1 set class_ 1
$ns attach-agent $n0 $tcp1
$ns attach-agent $n4 $sink1
$ns connect $tcp1 $sink1

#setup a FTP Application
set ftp1 [new Application/FTP]
$ftp1 attach-agent $tcp1

#Schedule events for the CBR and FTP agents
$ns at 0.0 "$ftp1 start"
$ns at 4.0 "$cbr0 start"
$ns at 20.0 "$ftp1 stop"
$ns at 20.0 "$cbr0 stop"

$ns at 20.0 "finish"
$ns run

