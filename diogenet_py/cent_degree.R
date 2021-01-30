library(causaleffect)

g = parse.graphml('C://Users//elinarezv//Sources//diogenet//diogenet_py//g.graphml')

degree = as.numeric(format(igraph::centralization.degree(g)$centralization[1],digits = 3, nsmall = 3))

fileConn<-file("C://Users//elinarezv//Sources//diogenet//diogenet_py//degree.val")

writeLines(as.character(degree), fileConn)

close(fileConn)