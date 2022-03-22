library(causaleffect)

g = parse.graphml('C://Users//elinarezv//Sources//diogenet//diogenet_py//g.graphml')

eigenvector = as.numeric(format(igraph::centralization.evcent(g)$centralization[1],digits = 3, nsmall = 3))

fileConn<-file("C://Users//elinarezv//Sources//diogenet//diogenet_py//eigenvector.val")

writeLines(as.character(eigenvector), fileConn)

close(fileConn)