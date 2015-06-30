def distance( a, b ): return sum ( [ (x1-x2)**2 for x1,x2 in zip( a, b ) ] ) ** .5

def line_function( (x1,y1), (x2, y2) ):
    # Parametric equations expressing a line containing two points (x1, y1) and (x2, y2).
    X = lambda t: t*(x2-x1) + x1
    Y = lambda t: t*(y2-y1) + y1

    def line(x, y):
        dx, dy = x2-x1, y2-y1

        # Take the better parameterization.
        if abs(dx) > abs(dy):
            t = (x-x1) / dx
        else:
            t = (y-y1) / dy

        return X(t), Y(t)

    return line

def close_to( u, v ):
    EPSILON = 40
    return distance( u, v ) < EPSILON

def within_bounds( p1, p2, (x,y) ):
    (x1, y1), (x2, y2) = p1, p2
    dx, dy = x2-x1, y2-y1

    # More horizontal than vertical
    if abs(dx) > abs(dy):
        return x1 < x < x2 or x2 < x < x1
    else: # More vertical than horizontal
        return y1 < y < y2 or y2 < y < y1

def find_segment( self, pos ):
    segmentation = self.points
    for i in range( len(segmentation) - 1 ):

        # Make sure pos is within the bounds of the segmentation.
        #if within_bounds( self.get_start(), self.get_end(), pos ):
        if True:
            a, b = segmentation[i], segmentation[i+1]
        
            # Generate the equation of the line between a and b.
            F    = line_function( a, b )

            # See if pos is close enough to the segment to be considered touching.
            if close_to( pos, F(*pos) ):
                return a, b

    # If no segment matched, the pos wasn't on the segmentation.
    raise AssertionError


from math import cos, atan

def slope( (x1,y1), (x2, y2) ):
    try:
        m = (y2-y1) / (x2-x1)
    except ZeroDivisionError:
        # For a vertical line, approximate the slope with a big number.
        m = 100000
    return m

def split_segment( seg, pos ):
    x, y = pos
    a, b = seg

    GAP  = 5 * ( cos( atan( slope( a, b ) ) ) )

    # line drawn right to left
    if a[0] > b[0]:
        x1 = x+GAP
        x2 = x-GAP
        if x1 > a[0]:
            x1 = a[0]
        if x2 < b[0]:
            x2 = b[0]

    else:
    # line drawn left to right
        x1 = x-GAP
        x2 = x+GAP
        if x1 < a[0]:
            x1 = a[0]
        if x2 > b[0]:
            x2 = b[0]

    F   = line_function( a, b )

    return [ [a, F(x1, y)], [F(x2, y), b] ]

def segs_before( self, seg ):
    a, b         = seg
    segmentation = [ p for p in self.points ]
    for i in range( len(segmentation) - 1 ):
        k, l     = segmentation[i], segmentation[i+1]
        if (a,b) == (k,l):
            return segmentation[:i]
    return []

def segs_after( self, seg ):
    a, b         = seg
    segmentation = [ p for p in self.points ]
    for i in range( len(segmentation) - 1 ):
        k, l     = segmentation[i], segmentation[i+1]
        if (a,b) == (k,l):
            return segmentation[i+1+1:]
    return []
