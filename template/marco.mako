Process ${name}
%if pid:
with PID ${pid}
    %if memory_percent > thresholds[ 'memory_percent' ]:
excceded the memory threshold ${thresholds[ 'memory_percent' ]} with ${memory_percent}
    %endif
    %if cpu_percent > thresholds[ 'cpu_percent' ]:
excceded the CPU threshold ${thresholds[ 'cpu_percent' ]} with ${cpu_percent}
    %endif
%else:
${name} failed
%endif