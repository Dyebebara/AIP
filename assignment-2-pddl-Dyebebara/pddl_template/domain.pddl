(define (domain TramNetwork)
(:requirements
    :typing
    :negative-preconditions
)

(:types
    tram track
)

(:predicates
    ;Route S Tram location
    (at-stram ?loc - track)
    ;Tram is on a particular track
    (tram-at ?t - track)
    ;Tram is located at a particular track
    (tram-located-at ?t - tram ?track - track)
    ;Track switched to a particular destination
    (track-switched ?from ?to - track)
    ;Track able to be connected to a particular destination
    (track-connected ?from ?to - track)
    ;Track hasn't been visited yet
    (track-unvisited ?loc - track)
    ;Used for animation only
    (is-track ?t - track)
)

;The Route S Tram can move if
;  - The Route S Tram is at the current location,
;  - The Track is switched to the destination,
;  - There is no Tram at the destination,
;  - The Route S Tram hasn't visited the destination before.
;Effects: Move the Route S Tram to the destination and mark the current location
;  as visited.
(:action move
    :parameters (?from ?to - track)
    :precondition (and 
                        (at-stram ?from)
                        (track-connected ?from ?to )
                        (track-switched ?from ?to)
                        (not(tram-at ?to))
                        (track-unvisited ?to    ) 

    )
    :effect (and 
                    (at-stram ?to)
                    (not (at-stram ?from))
                    (not (track-unvisited ?to))

    )
)

;The Route S Tram can request a tram in its following destination to move to
; the following tram's switched track if
;  - The Route S Tram is at the current location before the Tram it is 
;    asking to move,
;  - The Tram requested to be moved is in the switched location for the Route S
;    Tram,
;  - There is no Tram at the destination.
;  - The Route S Tram is not at the destination.
;Effects: Move the Tram on the following track to its following destination.
(:action request
    :parameters (?before ?from - track ?tram - tram ?to - track)
    :precondition (and 
                        (at-stram ?before)
                        (tram-at ?from)
                        (tram-located-at ?tram ?from)
                        (track-switched ?from ?to)
                        (track-switched ?before ?from)
                        (not (tram-at ?to))
                        (not (at-stram ?to))
     )
    :effect (and 
                    (tram-at ?to)
                    (not (tram-at ?from))
                    (tram-located-at ?tram ?to)
                    (not (tram-located-at ?tram ?from))
    )
)

;The Route S Tram can switch the track it is currently on from its old 
; destination to a new destination track if
;  - The Route S Tram is at the Current Track,
;  - The Current Track is conneced to the new track,
;  - The Current Track is not already switched to the new location,
;Effects: Switch the track to the new location
(:action switch
    :parameters (?current ?old ?new - track)
    :precondition (and 
                        (at-stram ?current)
                        (track-switched ?current ?old)
                        (track-connected ?current ?new)
                        (not(track-switched ?current ?new))
                        (track-connected ?current ?old)  
    )
    :effect (and 
                    (track-switched ?current ?new)
                    (not(track-switched ?current ?old))
    )
)

)