library(igraphr)

read_graphml = function(x) {

    g<-read.graph(x, format = "graphml")
    return(g)
}
