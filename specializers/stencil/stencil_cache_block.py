import asp.codegen.cpp_ast as cpp_ast
import asp.codegen.ast_tools as ast_tools


class StencilCacheBlocker(object):
    """
    Class that takes a tree of perfectly-nested For loops (as in a stencil) and performs standard cache blocking
    on them.  Usage: StencilCacheBlocker().block(tree, factors) where factors is a tuple, one for each loop nest
    in the original tree.
    """
    class StripMineLoopByIndex(ast_tools.NodeTransformer):
        """Helper class that strip mines a loop of a particular index in the nest."""
        def __init__(self, index, factor):
            self.current_idx = -1
            self.target_idx = index
            self.factor = factor
            super(StencilCacheBlocker.StripMineLoopByIndex, self).__init__()
            
        def visit_For(self, node):
            self.current_idx += 1

            print "Searching for loop %d, currently at %d" % (self.target_idx, self.current_idx)

            if self.current_idx == self.target_idx:
                print "Before blocking:"
                print node
                
                return ast_tools.LoopBlocker().loop_block(node, self.factor)
            else:
                return cpp_ast.For(node.loopvar,
                           node.initial,
                           node.end,
                           node.increment,
                           self.visit(node.body))
            
    def block(self, tree, factors):
        """Main method in StencilCacheBlocker.  Used to block the loops in the tree."""
        # first we apply strip mining to the loops given in factors
        for x in xrange(len(factors)):
            print "Doing loop %d by %d" % (x*2, factors[x])

            # we may want to not block a particular loop, e.g. when doing Rivera/Tseng blocking
            if factors[x] > 0:
                tree = StencilCacheBlocker.StripMineLoopByIndex(x*2, factors[x]).visit(tree)
            print tree

        # now we move all the outer strip-mined loops to be outermost
        for x in xrange(1,len(factors)):
            if factors[x] > 0:
                tree = self.bubble(tree, 2*x, x)
    
        return tree
        
    def bubble(self, tree, index, new_index):
        """
        Helper function to 'bubble up' a loop at index to be at new_index (new_index < index)
        while preserving the ordering of the loops between index and new_index.
        """
        for x in xrange(index-new_index):
            print "In bubble, switching %d and %d" % (index-x-1, index-x)
            ast_tools.LoopSwitcher().switch(tree, index-x-1, index-x)
        return tree
