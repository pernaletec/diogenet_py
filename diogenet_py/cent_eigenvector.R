library(causaleffect)

g = parse.graphml('C://Users//Ivanyk//Documents//proyectos//src//diogenet_py//diogenet_py//g.graphml')

eigenvector = as.numeric(format(igraph::centralization.evcent(g)$centralization[1],digits = 3, nsmall = 3))

fileConn<-file("eigenvector.val")

writeLines(as.character(eigenvector), fileConn)

close(fileConn)