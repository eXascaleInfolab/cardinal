
def error(estimates, Truth):
    #remove infinite values
    estimates = list(filter(lambda x: x != float('Inf'), estimates))
    n = len(estimates)
    s = [ (abs(estimates[i] - Truth) * (i + 1)) for i in range(n)]
    return 2 * sum(s) / (n * (n+1))

def conv(estimates, distincts):
    # window size
    w = 4
    #remove infinite values
    estimates = list(filter(lambda x: x != float('Inf'), estimates))
    n = len(estimates) 
    # bail out if not enough samples
    if n < w:
        return 1 
    s = [ (abs(estimates[i] - distincts[i]) / distincts[i]) for i in range(n-w, n)] #again, mind the indices.

    return sum(s) / w
