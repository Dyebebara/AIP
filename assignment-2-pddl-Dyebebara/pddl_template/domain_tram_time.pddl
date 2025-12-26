(define (domain TramNetwork)
(:requirements
    :typing
    :negative-preconditions
)

(:types
    stram tram track
)

(:predicates
    ;Route S Tram location with which stram
    (at-stram ?loc - track ?stram -stram)
    ;Tram is on a particular track
    (tram-at ?t - track)
    ;Tram is located at a particular track
    (tram-located-at ?t - tram ?track - track)
    ;Track switched to a particular destination
    (track-switched ?from ?to - track)
    ;Track able to be connected to a particular destination
    (track-connected ?from ?to - track)
    ;Track hasn't been visited yet
    (stram-unvisited ?loc - track ?s - stram)

    ; turn-base 判断回合用
    (stram-done ?stram - stram)
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
    :parameters (?from ?to - track ?stram - stram)
    :precondition (and 
                        (at-stram ?from ?stram)
                        (track-connected ?from ?to )
                        (track-switched ?from ?to)
                        (not(tram-at ?to))
                        (stram-unvisited ?to ?stram)
                        ;必须是未到轮次的stram
                        (not(stram-done ?stram))
                        ;排除其他stram在to的位置上卡住
                        (forall(?st - stram)(not(at-stram ?to ?st)))


    )
    :effect (and 
                    (at-stram ?to ?stram)
                    (not (at-stram ?from ?stram))
                    (not (stram-unvisited ?to ?stram))
                    (stram-done ?stram)


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
    :parameters (?before ?from - track ?tram - tram ?to - track ?stram - stram)
    :precondition (and 
                        (at-stram ?before ?stram)
                        (tram-located-at ?tram ?from)
                        (track-switched ?from ?to)
                        (track-switched ?before ?from)
                        (not (tram-at ?to))
                        (not (at-stram ?to ?stram))
                        ;stram还没操作
                        (not (stram-done ?stram))
                        ;没卡住
                        (forall(?st - stram)(not(at-stram ?to ?st)))



     )
    :effect (and 
                    (tram-at ?to)
                    (not (tram-at ?from))
                    (tram-located-at ?tram ?to)
                    (not (tram-located-at ?tram ?from))
                    (stram-done ?stram)


    )
)

;The Route S Tram can switch the track it is currently on from its old 
; destination to a new destination track if
;  - The Route S Tram is at the Current Track,
;  - The Current Track is conneced to the new track,
;  - The Current Track is not already switched to the new location,
;Effects: Switch the track to the new location
(:action switch
    :parameters (?current ?old ?new - track ?stram - stram)
    :precondition (and 
                        (at-stram ?current ?stram)
                        (track-switched ?current ?old)
                        (track-connected ?current ?new)
                        (not(track-switched ?current ?new))
                        (track-connected ?current ?old)  
                        (not (stram-done ?stram))
    )
    :effect (and 
                    (track-switched ?current ?new)
                    (not(track-switched ?current ?old))
                    (stram-done ?stram)
    )
)

(:action   new-turn
    :parameters ()
    :precondition (
                    forall(?stram - stram)(stram-done ?stram)
    )
    :effect (
                    forall(?stram - stram)(not(stram-done ?stram))

    )
)

(:action wait
    :parameters (?stram - stram)
    :precondition (and
                        (not(stram-done ?stram))
     )
    :effect (and 
                    (stram-done ?stram)


    )
)



)