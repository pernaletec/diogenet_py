library(causaleffect)

g = parse.graphml('C://Users//Ivanyk//Documents//proyectos//src//diogenet_py//diogenet_py//g.graphml')

betweenness = as.numeric(format(igraph::centralization.betweenness(g)$centralization[1],digits = 3, nsmall = 3))

fileConn<-file("betweenness.val")

writeLines(as.character(betweenness), fileConn)

close(fileConn)