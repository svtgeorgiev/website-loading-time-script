# read the metrics from the file and write them to the metrics file
def write_metrics():
    with open(r'C:\scripts\metrics.txt', 'r') as f:
        with open(r'path to file\metrics.prom', 'w') as metrics_file:
            for line in f:
                if line.startswith('#'):
                    # don't read comment lines
                    continue
                name, value = line.strip().split()
                if name == 'my_metric':
                    # write to metrics file
                    metrics_file.write(f'my_metric {value}\n')


# function write the metrics one time
write_metrics()
