#n <- 1e3
#for(i in 1:10)
#{
#  qr.solve(matrix(runif(n*n), nrow = n), seq_len(n)/(n+1))  
#}
library(causaleffect)
a = parse.graphml('C://Users//Ivanyk//Documents//proyectos//src//diogenet_py//diogenet_py//grafo1.graphml')
degree = as.numeric(format(igraph::centralization.degree(a)$centralization[1],digits = 3, nsmall = 3))
fileConn<-file("output.txt")
writeLines(as.character(degree), fileConn)
close(fileConn)

