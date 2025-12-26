;It is recommended that you install the misc-pddl-generators plugin 
;and then use the Network generator to create the graph
(define (problem p1-network)
    (:domain TramNetwork)
    (:objects
        track0 track1 track2 track3 track4 track5 track6 track7 track8 track9 - track
        tram1 tram2 - tram
        stram1 stram2 - stram
    )
    (:init
        ; Initial Route S Tram Location
        (at-stram track0 stram1)
        (at-stram track5 stram2)

        ; Initial Locations of Trams
        (tram-located-at tram1 track3)
        (tram-located-at tram2 track7)

        ; Initial Locations filled with Trams
        (tram-at track3)
        (tram-at track7)



        ; Track connections (Insert -> Network)        
        ;; make sure these are constants or objects:
        ;; track0 track4 track3 track6 track8 track7
        (track-connected track0 track4)
        ; (track-connected track4 track3)
        (track-connected track3 track6)
        (track-connected track6 track8)
        (track-connected track7 track6)
        (track-connected track3 track4)
        (track-connected track0 track2)
        (track-connected track2 track3)
        (track-connected track3 track7)
        (track-connected track7 track9)
        (track-connected track5 track4)
        (track-connected track4 track9)
        (track-connected track4 track1)
        (track-connected track1 track2)
        
        ; Track initial switching   
        ;; make sure these are constants or objects:
        ;; track0 track2 track3 track7 track9 track5 track4 track1
        (track-switched track0 track2)
        (track-switched track2 track3)
        (track-switched track3 track7)
        (track-switched track7 track9)
        (track-switched track5 track4)
        (track-switched track4 track9)
        (track-switched track4 track1)
        (track-switched track1 track2)
        
        
        
        
        
        ; All Tracks initially unvisited
        (stram-unvisited track0 stram2)
        (stram-unvisited track1 stram1)
        (stram-unvisited track1 stram2)
        (stram-unvisited track2 stram1)
        (stram-unvisited track2 stram2)
        (stram-unvisited track3 stram1)
        (stram-unvisited track3 stram2)
        (stram-unvisited track4 stram1)
        (stram-unvisited track4 stram2)
        (stram-unvisited track5 stram1)

        (stram-unvisited track6 stram1)
        (stram-unvisited track6 stram2)
        (stram-unvisited track7 stram1)
        (stram-unvisited track7 stram2)
        (stram-unvisited track8 stram1)
        (stram-unvisited track8 stram2)
        (stram-unvisited track9 stram1)
        (stram-unvisited track9 stram2)
      

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
    )
    (:goal (and
        ; Final Route S Tram Location
               (at-stram track2 stram2)
               (at-stram track9 stram1)
    ))
)