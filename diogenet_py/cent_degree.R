library(causaleffect)

g = parse.graphml('C://Users//Ivanyk//Documents//proyectos//src//diogenet_py//diogenet_py//g.graphml')

degree = as.numeric(format(igraph::centralization.degree(g)$centralization[1],digits = 3, nsmall = 3))

fileConn<-file("degree.val")

writeLines(as.character(degree), fileConn)

close(fileConn)