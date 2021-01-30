library(causaleffect)

g = parse.graphml('C://Users//elinarezv//Sources//diogenet//diogenet_py//g.graphml')

closeness = as.numeric(format(igraph::centralization.closeness(g)$centralization[1],digits = 3, nsmall = 3))

fileConn<-file("C://Users//elinarezv//Sources//diogenet//diogenet_py//closeness.val")

writeLines(as.character(closeness), fileConn)

close(fileConn)