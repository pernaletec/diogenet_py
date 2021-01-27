n <- 1e3
for(i in 1:10)
{
  qr.solve(matrix(runif(n*n), nrow = n), seq_len(n)/(n+1))  
}
