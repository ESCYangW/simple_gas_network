### Simple Gas Network Design Problem
>  The toy project was proposed by Dr Sheila Samsatli

Consider the geographical region that has been discretised into cells as in the diagram below.
The co-ordinates (in km relative to an origin) of the centre of each cell are:

| Cell	| X co-ord	| Y co-ord |
|--------|-----------|----------|
|1|	0	|0|
|2	|50	|0|
|3	|100	|0|
|4	|150	|0|
|5	|200	|0|
|6	|100	|50|
|7	|150	|50|
|8	|200	|50|
|9	|100	|100|
|10	|150	|100|
|11	|200	|100|
|12	|150	|150|
|13	|200	|150|
|14	|250	|150|

 
The population estimate for each cell is: 

|Cell	|Population|
|------|---------|
|1	|850000|
|2	|620000|
|3	|650000|
|4	|940000|
|5	|500000|
|6	|710000|
|7	|940000|
|8	|960000|
|9	|820000|
|10	|500000|
|11	|980000|
|12	|340000|
|13	|210000|
|14	|240000|

It is assumed that the natural gas demand per person per day is 2 m<sup>3</sup> at standard temperature and pressure (STP). Cell 1 has a supply terminal which can cope with a maximum throughput of 22,000,000 m<sup>3</sup> / day.

Your objective is to design an optimal gas distribution network, by developing a mathematical optimisation model which determines:
> a.	The network infrastructure with the current single supply point (cell 1).
> 
> b.	In which cell of the possible ship-accessible cells (all but 10 and 7) to install another supply terminal which will be able to supply a gas grid with gas derived from LNG. You should identify the cost reduction achieved (if any) through the installation of this new supply point

You should compare solutions that minimise capital cost and those that minimise operating cost and make recommendations for the design of the network. Feel free to undertake any further investigations (e.g. attempting to balance capital and operating cost) you feel may be useful.

Data
Capital cost
The capital cost of installing a gas pipeline can (in the first instance) be assumed to be independent of pipeline capacity and to be £1m per km.

Operating cost
The operating cost is in practice a complex function of flow and distance since it primarily relates to the cost of re-compression. For this exercise, it will be assumed proportional to the product of flow and distance, and a value of £0.15 per 1000 m<sup>3</sup> &middot; km can be assumed.

You may assume that the length of a pipe between cells is equal to the Euclidean distance between their centres.

Modelling strategy
The key is to define binary variables which denote whether a link between a pair of cells exists. This will then allow flow to occur between the cells. This requires a flow material balance equation. You should develop a mixed integer linear program in AIMMS to solve this.

> Dr Yang Wang coded in python using open-source env pyomo for this problem.
