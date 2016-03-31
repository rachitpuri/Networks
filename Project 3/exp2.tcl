# Create a ns object
set ns [new Simulator]
$ns color 1 Blue
$ns color 2 Red

# Open the Trace files
set TraceFile [open exp2.tr w]
$ns trace-all $TraceFile

proc finish {} {
	global ns TraceFile
	$ns flush-trace
	close $TraceFile
	#exec nam outtcp2.nam &
	exit 0
}

# Create six nodes
set n0 [$ns node]
set n1 [$ns node]
set n2 [$ns node]
set n3 [$ns node]
set n4 [$ns node]
set n5 [$ns node]

set version1 [lindex $argv 0]
set version2 [lindex $argv 1]
set speed [lindex $argv 2]

$ns duplex-link $n0 $n2 10Mb 10ms DropTail
$ns duplex-link $n1 $n2 10Mb 10ms DropTail
$ns duplex-link $n2 $n3 10Mb 10ms DropTail 
$ns duplex-link $n3 $n4 10Mb 10ms DropTail
$ns duplex-link $n3 $n5 10Mb 10ms DropTail


$ns duplex-link-op $n0 $n2 orient right-down
$ns duplex-link-op $n1 $n2 orient right-up
$ns duplex-link-op $n2 $n3 orient right
$ns duplex-link-op $n3 $n4 orient right-up
$ns duplex-link-op $n3 $n5 orient right-down

#Create a UDP agent and attach it to node n2
set udp0 [new Agent/UDP]
$ns attach-agent $n2 $udp0

# Create a CBR traffic source and attach it to udp0
set cbr0 [new Application/Traffic/CBR]
$cbr0 set rate_ ${speed}Mb
$cbr0 attach-agent $udp0

set null0 [new Agent/Null] 
$ns attach-agent $n3 $null0

$ns connect $udp0 $null0

if {$version1 eq "Vegas"} {
	set tcp1 [new Agent/TCP/Vegas]
} elseif {$version1 eq "Reno"} {
	set tcp1 [new Agent/TCP/Reno]
} elseif {$version1 eq "Newreno"} {
	set tcp1 [new Agent/TCP/Newreno]
} elseif {$version1 eq "Tahoe"} {
	set tcp1 [new Agent/TCP]
}

if {$version2 eq "Vegas"} {
        set tcp2 [new Agent/TCP/Vegas]
} elseif {$version2 eq "Reno"} {
        set tcp2 [new Agent/TCP/Reno]
} elseif {$version2 eq "Newreno"} {
        set tcp2 [new Agent/TCP/Newreno]
} elseif {$version2 eq "Tahoe"} {
        set tcp2 [new Agent/TCP]
}


$ns attach-agent $n0 $tcp1
set sink1 [new Agent/TCPSink/DelAck]
$ns attach-agent $n4 $sink1
$ns connect $tcp1 $sink1

$ns attach-agent $n1 $tcp2
set sink2 [new Agent/TCPSink/DelAck]
$ns attach-agent $n5 $sink2
$ns connect $tcp2 $sink2

#TCP N0 and N4
set ftp1 [new Application/FTP]
$ftp1 attach-agent $tcp1
$ftp1 set type_ FTP

#TCP N1 and N5
set ftp2 [new Application/FTP]
$ftp2 attach-agent $tcp2
$ftp2 set type_ FTP


$ns at 0 "$ftp1 start"
$ns at 0 "$cbr0 start"
$ns at 0 "$ftp2 start"
$ns at 20 "$ftp1 stop"
$ns at 20 "$cbr0 stop"
$ns at 20 "$ftp2 stop"

$ns at 20 "finish"
$ns run

