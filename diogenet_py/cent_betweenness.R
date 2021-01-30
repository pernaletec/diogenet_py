library(causaleffect)

g = parse.graphml('C://Users//elinarezv//Sources//diogenet//diogenet_py//g.graphml')

betweenness = as.numeric(format(igraph::centralization.betweenness(g)$centralization[1],digits = 3, nsmall = 3))

fileConn<-file("C://Users//elinarezv//Sources//diogenet//diogenet_py//betweenness.val")

writeLines(as.character(betweenness), fileConn)

close(fileConn)