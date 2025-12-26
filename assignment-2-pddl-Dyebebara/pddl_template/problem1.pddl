;It is recommended that you install the misc-pddl-generators plugin 
;and then use the Network generator to create the graph
(define (problem p1-network)
    (:domain TramNetwork)
    (:objects
        track0 track1 track2 track3 track4 track5 track6 track7 track8 - track
        tram1 tram2 tram3 - tram
    )
    (:init
        ; Initial Route S Tram Location
        (at-stram track0)

        ; Initial Locations of Trams
        (tram-located-at tram1 track2)
        (tram-located-at tram2 track4)
        (tram-located-at tram3 track5)

        ; Initial Locations filled with Trams
        (tram-at track2)
        (tram-at track4)
        (tram-at track5)

        ; Track connections (Insert -> Network)        
        ;; make sure these are constants or objects:
        ;; track0 track1 track2 track4 track5 track6 track3 track8 track7 track
        (track-connected track0 track1)
        (track-connected track1 track2)
        (track-connected track2 track4)
        (track-connected track4 track5)
        (track-connected track5 track6)
        (track-connected track1 track3)
        (track-connected track3 track8)
        (track-connected track8 track7)
        (track-connected track3 track4)
        (track-connected track8 track5)
        
        
        ; Track initial switching   
        ;; make sure these are constants or objects:
        ;; track0 track1 track2 track4 track5 track6 track3 track8 track7
        (track-switched track0 track1)
        (track-switched track1 track2)
        (track-switched track2 track4)
        (track-switched track4 track5)
        (track-switched track5 track6)
        (track-switched track3 track8)
        (track-switched track8 track7)
        
        
        
        
        
        
        ; All Tracks initially unvisited
        (track-unvisited track1)
        (track-unvisited track2)
        (track-unvisited track3)
        (track-unvisited track4)
        (track-unvisited track5)
        (track-unvisited track6)
        (track-unvisited track7)
        (track-unvisited track8)
      
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
    )
    (:goal (and
        ; Final Route S Tram Location
               (at-stram track5)
    ))
)