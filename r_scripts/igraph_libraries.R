library(causaleffect)

get_betweenness <- function(graph){
    g = parse.graphml(graph)
    betweenness = as.numeric(format(igraph::centralization.betweenness(g)$centralization[1],digits = 3, nsmall = 3))

    return (betweenness)
}

get_closeness <- function(graph){
    g = parse.graphml(graph)
    closeness = as.numeric(format(igraph::centralization.closeness(g)$centralization[1],digits = 3, nsmall = 3))

    return (closeness)
}

get_degree <- function(graph){
    g = parse.graphml(graph)
    degree = as.numeric(format(igraph::centralization.degree(g)$centralization[1],digits = 3, nsmall = 3))

    return (degree)
}

get_eigenvector <- function(graph){
    g = parse.graphml(graph)
    eigenvector = as.numeric(format(igraph::centralization.evcent(g)$centralization[1],digits = 3, nsmall = 3))

    return (eigenvector)
}

