;It is recommended that you install the misc-pddl-generators plugin 
;and then use the Network generator to create the graph
(define (problem p2-network)
    (:domain TramNetwork)
    (:objects
        track0 track1 track2 track3 track4 track5 track6 track7 track8 track9 track10 track11 track12 track13 track14 track15 track16 track17 track18 track19 - track
        tram1 tram2 tram3 tram4 tram5 tram6 tram7 tram8 - tram
    )
    (:init
        ; Initial Route S Tram Location
        (at-stram track0)

        ; Initial Locations of Trams
        (tram-located-at tram1 track1)
        (tram-located-at tram2 track2)
        (tram-located-at tram3 track5)  
        (tram-located-at tram4 track6)
        (tram-located-at tram5 track7)
        (tram-located-at tram6 track11) 
        (tram-located-at tram7 track13)
        (tram-located-at tram8 track16)
          
        ; Initial Locations filled with Trams
        (tram-at track1)
        (tram-at track2)
        (tram-at track5)
        (tram-at track6)
        (tram-at track7)
        (tram-at track11)
        (tram-at track13)
        (tram-at track16)



        ; Track connections (Insert -> Network) ; 理论上是相连的情况
        ; 0 1 2 3 4
        ; 5 6 7
        ; 5 10 15 16 17 18 19 14 9
        ; 11 12 7 2
        ; 13 8 3
        ; 0 5
        ; 1 6
        ; 11 6
        ; 11 16
        ; 16 11
        ; 12 17
        ; 10 11
        ; 12 13
        ; 9 4
        ; 9 8






        ;; make sure these are constants or objects:
        ;; track0 track1 track2 track3 track4 track5 track6 track7 track10 track15 track16 track17 track18 track19 track14 track9 track11 track12 track13 track8
        (track-connected track0 track1)
        (track-connected track1 track2)
        (track-connected track2 track3)
        (track-connected track3 track4)
        (track-connected track5 track6)
        (track-connected track6 track7)
        (track-connected track5 track10)
        (track-connected track10 track15)
        (track-connected track15 track16)
        (track-connected track16 track17)
        (track-connected track17 track18)
        (track-connected track18 track19)
        (track-connected track19 track14)
        (track-connected track14 track9)
        (track-connected track11 track12)
        (track-connected track12 track7)
        (track-connected track7 track2)
        (track-connected track13 track8)
        (track-connected track8 track3)
        (track-connected track0 track5)
        (track-connected track1 track6)
        (track-connected track11 track6)
        (track-connected track11 track16)
        (track-connected track16 track11)
        (track-connected track12 track17)
        (track-connected track10 track11)
        (track-connected track12 track13)
        (track-connected track9 track4)
        (track-connected track9 track8)
        

        

        ; Track initial switching ; 实际上是相连的情况
        ; 0 1 2 3 4
        ;5 6 7
        ;5 10 15 16 17 18 19 14 9
        ;11 12 7 2
        ;13 8 3
        ;9 8

        ;; make sure these are constants or objects:
        ;; track0 track1 track2 track3 track4 track5 track6 track7 track10 track15 track16 track17 track18 track19 track14 track9 track11 track12 track13 track8
        (track-switched track0 track1)
        (track-switched track1 track2)
        (track-switched track2 track3)
        (track-switched track3 track4)
        (track-switched track5 track6)
        (track-switched track6 track7)
        (track-switched track5 track10)
        (track-switched track10 track15)
        (track-switched track15 track16)
        (track-switched track16 track17)
        (track-switched track17 track18)
        (track-switched track18 track19)
        (track-switched track19 track14)
        (track-switched track14 track9)
        (track-switched track11 track12)
        (track-switched track12 track7)
        (track-switched track7 track2)
        (track-switched track13 track8)
        (track-switched track8 track3)
        (track-switched track9 track8)



        ; All Tracks initially unvisited
        (track-unvisited track1)
        (track-unvisited track2)
        (track-unvisited track3)
        (track-unvisited track4)
        (track-unvisited track5)
        (track-unvisited track6)
        (track-unvisited track7)
        (track-unvisited track8)
        (track-unvisited track9)
        (track-unvisited track10)  
        (track-unvisited track11)
        (track-unvisited track12)
        (track-unvisited track13)
        (track-unvisited track14)
        (track-unvisited track15)
        (track-unvisited track16)
        (track-unvisited track17)
        (track-unvisited track18)
        (track-unvisited track19)


    )
    (:goal (and
        ; Final Route S Tram Location
        (at-stram track4)
    ))
)