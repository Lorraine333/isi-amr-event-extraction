#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Authors: Tim Henderson and Steve Johnson
#Email: tim.tadh@gmail.com, steve@steveasleep.com
#For licensing see the LICENSE file in the top level directory.

from __future__ import absolute_import
from __future__ import division
from six.moves import range
import re

import collections

try:
    import numpy as np
    zeros = np.zeros
    chararray = np.chararray
except ImportError:
    def py_zeros(dim, pytype):
        assert len(dim) == 2
        return [[pytype() for y in range(dim[1])]
                for x in range(dim[0])]
    zeros = py_zeros

try:
    from editdist import distance as strdist
except ImportError:
    def strdist(a, b):
        if a == b:
            return (-15)
        elif "r_value" in a and "r_value" in b:
            return 100
        elif re.search("^r_op[1-9]+_[a-zA-Z]+", a) and re.search("^r_op[1-9]+_[a-zA-Z]+", b):
            return 100
        else:
            return 10

from simple_tree import Node


class AnnotatedTree(object):

    def __init__(self, root, get_children):
        self.get_children = get_children

        # print "*"*30
        # print 'root',root
        # print "*"*30
        # print get_children(root)
        self.root = root
        self.nodes = list()  # a pre-order enumeration of the nodes in the tree
        self.ids = list()    # a matching list of ids
        self.lmds = list()   # left most descendents
        self.keyroots = None
            # k and k' are nodes specified in the pre-order enumeration.
            # keyroots = {k | there exists no k'>k such that lmd(k) == lmd(k')}
            # see paper for more on keyroots

        stack = list()
        pstack = list()
        stack.append((root, collections.deque()))
        j = 0
        while len(stack) > 0:
            n, anc = stack.pop()
            nid = j
            for c in self.get_children(n):
                a = collections.deque(anc)
                a.appendleft(nid)
                stack.append((c, a))
            pstack.append(((n, nid), anc))
            j += 1
        lmds = dict()
        keyroots = dict()
        i = 0
        while len(pstack) > 0:
            (n, nid), anc = pstack.pop()
            #print list(anc)
            self.nodes.append(n)
            self.ids.append(nid)
            # print n.label,nid,anc
            # print n.label, [a.label for a in anc]
            if not self.get_children(n):
                lmd = i
                for a in anc:
                    if a not in lmds: lmds[a] = i
                    else: break
            else:
                try: lmd = lmds[nid]
                except:
                    import pdb
                    pdb.set_trace()
            self.lmds.append(lmd)
            keyroots[lmd] = i
            # print keyroots
            i += 1
        self.keyroots = sorted(keyroots.values())


def simple_distance(A, B, get_children=Node.get_children,
        get_label=Node.get_label, label_dist=strdist):
    """Computes the exact tree edit distance between trees A and B.

    Use this function if both of these things are true:

    * The cost to insert a node is equivalent to ``label_dist('', new_label)``
    * The cost to remove a node is equivalent to ``label_dist(new_label, '')``

    Otherwise, use :py:func:`zss.distance` instead.

    :param A: The root of a tree.
    :param B: The root of a tree.

    :param get_children:
        A function ``get_children(node) == [node children]``.  Defaults to
        :py:func:`zss.Node.get_children`.

    :param get_label:
        A function ``get_label(node) == 'node label'``.All labels are assumed
        to be strings at this time. Defaults to :py:func:`zss.Node.get_label`.

    :param label_distance:
        A function
        ``label_distance((get_label(node1), get_label(node2)) >= 0``.
        This function should take the output of ``get_label(node)`` and return
        an integer greater or equal to 0 representing how many edits to
        transform the label of ``node1`` into the label of ``node2``. By
        default, this is string edit distance (if available). 0 indicates that
        the labels are the same. A number N represent it takes N changes to
        transform one label into the other.

    :return: An integer distance [0, inf+)
    """
    # return distance(
    #     A, B, get_children,
    #     insert_cost=lambda node: label_dist('', get_label(node)),
    #     remove_cost=lambda node: label_dist(get_label(node), ''),
    #     update_cost=lambda a, b: label_dist(get_label(a), get_label(b)),
    # )
    return distance(
        A, B, get_children,
        insert_cost=lambda node: 1*label_dist('', get_label(node)),
        remove_cost=lambda node: 1*label_dist(get_label(node), ''),
        update_cost=lambda a, b: 1*label_dist(get_label(a), get_label(b)),
    )


def distance(A, B, get_children, insert_cost, remove_cost, update_cost):
    '''Computes the exact tree edit distance between trees A and B with a
    richer API than :py:func:`zss.simple_distance`.

    Use this function if either of these things are true:

    * The cost to insert a node is **not** equivalent to the cost of changing
      an empty node to have the new node's label
    * The cost to remove a node is **not** equivalent to the cost of changing
      it to a node with an empty label

    Otherwise, use :py:func:`zss.simple_distance`.

    :param A: The root of a tree.
    :param B: The root of a tree.

    :param get_children:
        A function ``get_children(node) == [node children]``.  Defaults to
        :py:func:`zss.Node.get_children`.

    :param insert_cost:
        A function ``insert_cost(node) == cost to insert node >= 0``.

    :param remove_cost:
        A function ``remove_cost(node) == cost to remove node >= 0``.

    :param update_cost:
        A function ``update_cost(a, b) == cost to change a into b >= 0``.

    :return: An integer distance [0, inf+)
    '''
    A, B = AnnotatedTree(A, get_children), AnnotatedTree(B, get_children)
    treedists = zeros((len(A.nodes), len(B.nodes)), int)
    treepath = chararray((len(A.nodes), len(B.nodes)),itemsize=5000) 
    treepath[:] = ""
    # treepath = [[""]*len(B.nodes)]*len(A.nodes)

    def treedist(i, j):
        Al = A.lmds
        Bl = B.lmds
        An = A.nodes
        Bn = B.nodes
        A_num = A.ids
        B_num = B.ids

        m = i - Al[i] + 2
        n = j - Bl[j] + 2
        fd = zeros((m,n), int)
        fd_path = chararray((m, n),itemsize=5000)
        fd_path[:] = ""
        # fd_path = [[""]*n]*m


        ioff = Al[i] - 1
        joff = Bl[j] - 1

        for x in range(1, m): # δ(l(i1)..i, θ) = δ(l(1i)..1-1, θ) + γ(v → λ)
            # print 'remove',x,An[x+ioff].label
            fd_path[x,0] = fd_path[x-1,0] + "*Delete: " + An[x+ioff].label+'('+str(A_num[x+ioff])+')'
            fd[x][0] = fd[x-1][0] + remove_cost(An[x+ioff])
        for y in range(1, n): # δ(θ, l(j1)..j) = δ(θ, l(j1)..j-1) + γ(λ → w)
            # print 'insert',y, Bn[y+joff]
            fd_path[0,y] = fd_path[0,y-1] + "*Insert: " + Bn[y+joff].label+'('+str(B_num[y+joff])+')'
            fd[0][y] = fd[0][y-1] + insert_cost(Bn[y+joff])
        # print 'fd',fd
        # print 'fd_path',fd_path

        for x in range(1, m): ## the plus one is for the xrange impl
            for y in range(1, n):
                # only need to check if x is an ancestor of i
                # and y is an ancestor of j
                # print '*'*50
                if Al[i] == Al[x+ioff] and Bl[j] == Bl[y+joff]:
                    # print 'condition'
                    #                   +-
                    #                   | δ(l(i1)..i-1, l(j1)..j) + γ(v → λ)
                    # δ(F1 , F2 ) = min-+ δ(l(i1)..i , l(j1)..j-1) + γ(λ → w)
                    #                   | δ(l(i1)..i-1, l(j1)..j-1) + γ(v → w)
                    #                   +-
                    fd[x][y] = min(
                        fd[x-1][y] + remove_cost(An[x+ioff]),
                        fd[x][y-1] + insert_cost(Bn[y+joff]),
                        fd[x-1][y-1] + update_cost(An[x+ioff], Bn[y+joff]),
                    )
                    if fd[x][y] == fd[x-1][y-1] + update_cost(An[x+ioff], Bn[y+joff]):
                        if update_cost(An[x+ioff], Bn[y+joff]) != -15:
                            fd_path[x,y] = fd_path[x-1,y-1] + "*Rename: "+An[x+ioff].label+'('+str(A_num[x+ioff])+')'+' To '+ Bn[y+joff].label+'('+str(B_num[y+joff])+')'
                            # print 'update',An[x+ioff],'to', Bn[y+joff]
                            # print 'update',A_num[x+ioff],'to', B_num[y+joff]
                        else:
                            fd_path[x,y] = fd_path[x-1,y-1] + "*Match: "+An[x+ioff].label+'('+str(A_num[x+ioff])+')'+' and '+ Bn[y+joff].label+'('+str(B_num[y+joff])+')'

                    if fd[x][y] == fd[x][y-1] + insert_cost(Bn[y+joff]):
                        fd_path[x,y] = fd_path[x,y-1] + "*Insert: "+Bn[y+joff].label+'('+str(B_num[y+joff])+')'
                        # print 'insert',Bn[y+joff]

                    if fd[x][y] == fd[x-1][y] + remove_cost(An[x+ioff]):
                        fd_path[x,y] = fd_path[x-1,y]+"*Delete: "+An[x+ioff].label+'('+str(A_num[x+ioff])+')'
                        # print An[x+ioff]
                        # print 'remove',An[x+ioff]
                    
                    
                    treedists[x+ioff][y+joff] = fd[x][y]
                    treepath[x+ioff,y+joff] = fd_path[x,y]
                    # print 'fd',fd
                    # print 'fd_path',fd_path
                    # print 'treedists',treedists
                    # print 'treepath',treepath

                else:
                    # print 'not condition'
                    #                   +-
                    #                   | δ(l(i1)..i-1, l(j1)..j) + γ(v → λ)
                    # δ(F1 , F2 ) = min-+ δ(l(i1)..i , l(j1)..j-1) + γ(λ → w)
                    #                   | δ(l(i1)..l(i)-1, l(j1)..l(j)-1)
                    #                   |                     + treedist(i1,j1)
                    #                   +-
                    p = Al[x+ioff]-1-ioff
                    q = Bl[y+joff]-1-joff
                    #print (p, q), (len(fd), len(fd[0]))
                    fd[x][y] = min(
                        fd[x-1][y] + remove_cost(An[x+ioff]),
                        fd[x][y-1] + insert_cost(Bn[y+joff]),
                        fd[p][q] + treedists[x+ioff][y+joff]
                    )
                    if fd[x][y] == fd[x-1][y] + remove_cost(An[x+ioff]):
                        fd_path[x,y] = fd_path[x-1,y] + "*Delete: " + An[x+ioff].label+'('+str(A_num[x+ioff])+')'
                    if fd[x][y] == fd[x][y-1] + insert_cost(Bn[y+joff]):
                        fd_path[x,y] = fd_path[x,y-1] + "*Insert: " + Bn[y+joff].label+'('+str(B_num[y+joff])+')'
                    if fd[x][y] == fd[p][q] + treedists[x+ioff][y+joff]:
                        # print 'doing what???'
                        # print fd[p][q],p,q
                        # print x+ioff,y+joff
                        fd_path[x,y] = fd_path[p,q] + treepath[x+ioff,y+joff]
                    # print 'fd',fd
                    # print 'fd_path',fd_path
                    # print 'treedists',treedists
                    # print 'treepath',treepath
    # print A.keyroots
    # print B.keyroots
    # print A.ids
    # print B.ids

    # print 'Tree A'
    treeA = {}
    for i in range(len(A.nodes)):
        treeA[A.ids[i]] = A.nodes[i].label 
        # print node.label
    # print 'Tree B'

    treeB = {}
    for j in range(len(B.nodes)):
        treeB[B.ids[j]] = B.nodes[j].label

    # print A.nodes.label
    # print B.nodes.label
    for i in A.keyroots:
        for j in B.keyroots:
            treedist(i,j)
            # print i, j
            # print treedists
            # print treepath
    path = treepath[-1][-1]
    step = path.split("*")
    # for i in range step:
    #     if i[0] == "R":
    
    # print 
    # print "Path"
    path_result = []
    for temp in step[1:]:
        path_result.append(temp+";")
    print len(path_result)
    # print step[1:]
    # print   
    # print 'Distance:',treedists[-1][-1]
    return treeA, treeB, path_result, treedists[-1][-1]
