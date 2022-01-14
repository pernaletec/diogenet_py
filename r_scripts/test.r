#n <- 1e3
#for(i in 1:10)
#{
#  qr.solve(matrix(runif(n*n), nrow = n), seq_len(n)/(n+1))  
#}
library(causaleffect)

a = parse.graphml('C://Users//Ivanyk//Documents//proyectos//src//diogenet_py//diogenet_py//grafo1.graphml')

degree = as.numeric(format(igraph::centralization.degree(a)$centralization[1],digits = 3, nsmall = 3))
betweenness = as.numeric(format(igraph::centralization.betweenness(a)$centralization[1],digits = 3, nsmall = 3))
closeness = as.numeric(format(igraph::centralization.closeness(a)$centralization[1],digits = 3, nsmall = 3))
eigenvector = as.numeric(format(igraph::centralization.evcent(a)$centralization[1],digits = 3, nsmall = 3))

fileConn<-file("output.txt")

writeLines(c(as.character(degree),as.character(betweenness),as.character(closeness),as.character(eigenvector)), fileConn, sep = "\n")

close(fileConn)

