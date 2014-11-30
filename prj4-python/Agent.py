# Your Agent for solving Raven's Progressive Matrices. You MUST modify this file.
#
# You may also create and submit new files in addition to modifying this file.
#
# Make sure your file retains methods with the signatures:
# def __init__(self)
# def Solve(self,problem)
#
# These methods will be necessary for the project's main method to run.

import cv2
from pprint import pprint


class Agent:
    # The default constructor for your Agent. Make sure to execute any
    # processing necessary before your Agent starts solving problems here.
    #
    # Do not add any variables to this signature; they will not be used by
    # main().
    def __init__(self):
        # knowledge base - lets our Agent acquire and learn info from each problem
        self.kb = {}
        pass

    # The primary method for solving incoming Raven's Progressive Matrices.
    # For each problem, your Agent's Solve() method will be called. At the
    # conclusion of Solve(), your Agent should return a String representing its
    # answer to the question: "1", "2", "3", "4", "5", or "6". These Strings
    # are also the Names of the individual RavensFigures, obtained through
    # RavensFigure.getName().
    #
    # In addition to returning your answer at the end of the method, your Agent
    # may also call problem.checkAnswer(String givenAnswer). The parameter
    # passed to checkAnswer should be your Agent's current guess for the
    # problem; checkAnswer will return the correct answer to the problem. This
    # allows your Agent to check its answer. Note, however, that after your
    # agent has called checkAnswer, it will#not* be able to change its answer.
    # checkAnswer is used to allow your Agent to learn from its incorrect
    # answers; however, your Agent cannot change the answer to a question it
    # has already answered.
    #
    # If your Agent calls checkAnswer during execution of Solve, the answer it
    # returns will be ignored; otherwise, the answer returned at the end of
    # Solve will be taken as your Agent's answer to this problem.
    #
    # @param problem the RavensProblem your agent should solve
    # @return your Agent's answer to this problem
    def Solve(self, problem):
        ret = '6'
        
        problem = pythonize(problem)
        figures = problem['figures']
        
        # Debug code for jumping to specific problems
        # if not '2x2' in problem['name']:
        #     return '8'
        
        pprint(problem)
        print problem['name']
        self.scan_attrs(problem)
        
        choices = {}
        for i in range(1, 7):
            i = str(i)
            choices[i] = figures[i]
        
        # 2x1
        if problem['type'] == '2x1 (Image)':
            ret = self.solve_2x1(figures['A'], figures['B'], figures['C'], choices)
        
        # 2x2
        if problem['type'] == '2x2 (Image)':
            ret = self.solve_2x2(figures['A'], figures['B'], figures['C'], choices)
            
        # 3x3
        if problem['type'] == '3x3 (Image)':
            # cheap hack - just look at the bottom right quadrant and treat it like a 2x2
            ret = self.solve_2x2(figures['E'], figures['F'], figures['H'], choices)
        
        return ret

        
    def scan_attrs(self, prob):
        """Looks at the current problem's attributes, stores them in the KB"""
        
        # Keep track of the names of objects in the current problem
        # (useful to determine if attributes are referring to other objects)
        object_names = []
        for fig in prob['figures'].values():
            for object_name in fig.keys():
                if not object_name in object_names:
                    object_names.append(object_name)
        
        if not 'attributes' in self.kb:
            self.kb['attributes'] = {}
        
        attrs = self.kb['attributes']
        
        # process the attributes in the current problem
        for fig in prob['figures'].values():
            for obj in fig.values():
                for attr, subvalues in obj.items():
                    
                    if not isinstance(subvalues, (list, tuple)):
                        subvalues = [subvalues]
                    
                    if not attr in attrs:
                        attrs[attr] = {'values': [],
                                       'relative': 'unknown',
                                       'multi': 'unknown',
                                       'count': 0}
                    data = attrs[attr]
                    
                    data['count'] += 1
                    
                    if data['multi'] == 'unknown':
                        if len(subvalues) > 1:
                            data['multi'] = 'yes'
                        else:
                            data['multi'] = 'no'
                    else:
                        if len(subvalues) > 1 and data['multi'] == 'no':
                            data['multi'] = 'sometimes'
                        elif len(subvalues) == 1 and data['multi'] == 'yes':
                            data['multi'] = 'sometimes'
                    
                    # process each subvalue
                    values = data['values']
                    for subvalue in subvalues:
                        # check to see if this attr refers to other objects
                        relative = False
                        if subvalue in object_names:
                            relative = True
                            if data['relative'] == 'unknown':
                                data['relative'] = 'yes'
                            elif data['relative' ] == 'no':
                                data['relative'] = 'sometimes'
                        else:
                            if data['relative'] == 'unknown':
                                data['relative'] = 'no'
                            elif data['relative'] == 'yes':
                                data['relative'] = 'sometimes'
                        
                        # add this to the seen values if it isn't already
                        # in there and it isn't a relative value
                        if not relative and not subvalue in values:
                            values.append(subvalue)
        
        # update the kb's attribute priorities based upon frequency of encounters
    
        sorted_attrs = sorted(attrs.items(), key=lambda attr: attr[1]['count'], reverse=True)
        priorities = self.kb['attribute_priorities'] = []
        for attr in sorted_attrs:
            priorities.append(attr[0])
    
    
    def solve_2x2(self, A, B, C, choices):
        # remap B and C's parts to A's based on similarity
        B = self.get_renamed_figure(A, B)
        C = self.get_renamed_figure(A, C)
        
        x_target_rels = self.find_relationships(A, B)
        y_target_rels = self.find_relationships(A, C)
        
        print('A->B')
        pprint(x_target_rels)
        print('A->C')
        pprint(y_target_rels)
        
        scores = {}
        
        for i in range(1, 7):
            i = str(i)
            # remap choice's parts to C's based on similarity
            x_fig = self.get_renamed_figure(C, choices[i])
            x_choice_rels = self.find_relationships(C, x_fig)
            print('C->%s' % i)
            pprint(x_choice_rels)
            x_score = self.score_relationships(x_target_rels, x_choice_rels)
            print('Score: %f' % x_score)

            y_fig = self.get_renamed_figure(B, choices[i])
            y_choice_rels = self.find_relationships(B, y_fig)
            print('B->%s' % i)
            pprint(y_choice_rels)
            y_score = self.score_relationships(y_target_rels, y_choice_rels)
            print('Score: %f' % y_score)
            
            scores[i] = x_score + y_score
            
        
        scores = sorted(scores.items(), key=lambda score:score[1], reverse=True)
        pprint(scores)
        print 'choosing %s with score of %f' % (scores[0][0], scores[0][1])
        return scores[0][0]
    
    def solve_2x1(self, A, B, C, choices):
        old_b = B
        # remap B's parts to A's based on similarity
        B = self.get_renamed_figure(A, B)
        target_rels = self.find_relationships(A, B)
        print('A')
        pprint(A)
        if old_b != B:
            print('ORIGINAL B')
            pprint(old_b)
            
        print('REMAPPED B')
        pprint(B)
        print('A->B')
        pprint(target_rels)
        
        scores = {}
        
        for i in range(1, 7):
            i = str(i)
            old_fig = choices[i]
            # remap choice's parts to C's based on similarity
            choices[i] = self.get_renamed_figure(C, choices[i])
            choice_rels = self.find_relationships(C, choices[i])
            print('C->%s' % i)
            pprint(choice_rels)
            scores[i] = self.score_relationships(target_rels, choice_rels)
            print('Score: %f' % scores[i])
        
        scores = sorted(scores.items(), key=lambda score:score[1], reverse=True)
        pprint(scores)
        print 'choosing %s with score of %f' % (scores[0][0], scores[0][1])
        return scores[0][0]
    
    
    
    def get_renamed_figure(self, fig1, fig2):
        """Renames objects in fig2 based on analogies found from fig1 to fig2"""
        analogies = self.find_analogies(fig1, fig2)
        
        for obj2 in fig2:
            if not obj2 in analogies.values():
                analogies['_%s' % obj2] = obj2 # add an underscore to prevent name conflicts
        
        print "Analogies:"
        pprint(analogies)
        
        ret = {}
        
        for obj1, obj2 in analogies.items():
            if obj2 in fig2:
                ret[obj1] = fig2[obj2]
        
        return ret
        
        
    
    
    def find_analogies(self, fig1, fig2):
        """Finds analogies from fig1 to fig2. Recommend making fig1 the simpler fig."""
        
        if len(fig1) == 0 or len(fig2) == 0:
            return {}
        
        analogies = {} # map from fig1_name: (fig2_name, score)
        
        for obj1, attrs1 in fig1.items():
            matches = {}
            
            for obj2, attrs2 in fig2.items():
                score = 0
                max_score = 0
                
                for attr, value1 in attrs1.items():
                    cur_points = 1
                    if not attr in attrs2:
                        # doesn't exist in other object, skip it
                        continue
                    
                    if attr in self.kb['attribute_priorities']:
                        priority_rank = self.kb['attribute_priorities'].index(attr)
                        if priority_rank < 5:
                            cur_points += 2.0/(priority_rank + 1)


                    value2 = attrs2[attr]
                    if self.kb['attributes'][attr]['relative'] != 'no':
                        cur_points += 1
                        # this is a relative attribute, so names will be different
                        # just look at the length of the value
                        if len(value1) == len(value2):
                            score += cur_points
                    elif value1 == value2:
                        # exact match, increase score
                        score += cur_points
                    
                    max_score += cur_points
                        
                matches[obj2] = score / float(max_score)
            
            analogies[obj1] = sorted(matches.items(), key=lambda match: match[1], reverse=True)
        
        ret = {} # map from obj1: obj2
        
        while len(analogies) > 0:
            pprint(analogies)
            sorted_analogies = sorted(analogies.items(), key=lambda analogy: analogy[1][0][1], reverse=True)
            pprint(sorted_analogies)
            
            obj1 = sorted_analogies[0][0]
            obj2 = sorted_analogies[0][1][0][0]
            
            ret[obj1] = obj2
            del analogies[obj1]
            
            # remove obj2 from any other analogies findings
            for i in analogies.keys():
                for j in range(len(analogies[i]) - 1, -1, -1):
                    if analogies[i][j][0] == obj2:
                        del analogies[i][j]
                if len(analogies[i]) == 0:
                    del analogies[i]
            
        
        return ret
        
                
    def find_relationships(self, fig1, fig2):
        """Finds the relationships from fig1 to fig2."""
        
        rels = []
        
        # relationship based on # of objects
        if len(fig1) == len(fig2):
            rels.append({'obj': 'all', 'attr': 'count', 'type': 'match'})
        else:
            rels.append({'obj': 'all', 'attr': 'count', 'type': 'mismatch'})
        
        for obj, attrs in fig1.items():
            if not obj in fig2:
                # object has been removed in fig2
                rels.append({'obj': obj, 'attr': 'all', 'type': 'removed'})
                continue
        
        for obj in fig2:
            if not obj in fig1:
                # object is only present in fig2
                rels.append({'obj': obj, 'attr': 'all', 'type': 'added'})
                continue
            
            for attr in fig2[obj]:
                rel = {'obj': obj, 'attr': attr}
                
                if attr in fig1[obj] and fig1[obj][attr] == fig2[obj][attr]:
                    rel['type'] = 'match'
                else:
                    partial_match = False
                    for subvalue in fig2[obj][attr]:
                        if attr in fig1[obj] and subvalue in fig1[obj][attr]:
                            partial_match = True
                    
                    if partial_match:
                        rel['type'] = 'partial'
                    else:
                        rel['type'] = 'mismatch'
                        rel['old_values'] = ','.join(fig1[obj].get(attr, ['missing']))
                        rel['new_values'] = ','.join(fig2[obj][attr])
                        if rel['new_values'].isdigit() and rel['old_values'].isdigit():
                            rel['diff'] = float(rel['new_values']) - float(rel['old_values'])
                            del rel['old_values']
                            del rel['new_values']
                
                rels.append(rel)
        
        return rels
    

    def score_relationships(self, rels1, rels2):
        
        # keep track of score and max score to give a weighted result
        
        # one point if they have the same number of entries
        if len(rels1) == len(rels2):
            score = 1
        else:
            score = 0
        max_score = 1
        
        # look for each of the relationships from rels1 in rels2
        for rel in rels1:
            # assign the current points based upon the type of match
            if rel['type'] == 'match':
                cur_points = 1
            elif rel['type'] == 'mismatch':
                cur_points = 1
            else:
                cur_points = 0.25
            
            # give a bonus for higher "priority" attributes
            if rel['attr'] in self.kb['attribute_priorities']:
                priority_rank = self.kb['attribute_priorities'].index(rel['attr'])
                if priority_rank < 5:
                    cur_points += 1.0/(priority_rank + 1)
            
            max_score += cur_points
            
            if rel in rels2:
                score += cur_points
                
        
        # normalize score
        return score / float(max_score)
    


def visual_to_textual(img_file):
    """Returns a RavensFigure-like dictionary object from an image file"""
    
    fig = {}
    
    obj_count = 0
    
    img_gray = cv2.imread(img_file, cv2.CV_LOAD_IMAGE_GRAYSCALE)
    height, width = img_gray.shape
    
    # inverted threshold - OpenCV expects blackness to mean "nothing"
    ret, img_bw = cv2.threshold(img_gray, thresh=127, maxval=255, type=cv2.THRESH_BINARY_INV)
    
    #cv2.imshow('thresh', img_bw)
    contours, heir = cv2.findContours(img_bw, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_SIMPLE)
    
    #cv2.imshow('cnt', img_bw)
    
    #pprint(contours)
    #pprint(h)
    
    skips = []
    names = {}
    rects = {}
    
    for i in range(len(contours)):
        if i in skips:
            continue
            
        contour = contours[i]
        obj = {}
        circumference = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon=0.01*circumference, closed=True)
        
        # identify SHAPE
        num_sides = len(approx)
        obj['shape'] = get_shape_name(num_sides)
        
        
        # identify SIZE
        x,y,w,h = rect = cv2.boundingRect(contour)
        longest_side = max(w, h)
        if longest_side > 0.66 * width:
            obj['size'] = 'large'
        elif longest_side > 0.4 * width:
            obj['size'] = 'medium'
        else:
            obj['size'] = 'small'
        
        
        # identify FILLED
        if heir[0][i][2] != -1:
            # we have a child - determine if it's the same shape
            child_contour = contours[heir[0][i][2]]
            child_approx = cv2.approxPolyDP(child_contour, epsilon=0.01*cv2.arcLength(contour, True), closed=True)
            child_num_sides = len(child_approx)
            
            if (num_sides > 10 and child_num_sides > 10) \
                    or (num_sides == child_num_sides): # both the same shape
                # ignore the child, and mark the shape as unfilled
                skips += [heir[0][i][2]]
                obj['fill'] = 'no'
            else:
                # shape is filled and has *something else* inside
                obj['fill'] = 'yes'
        else:
            # object is filled
            obj['fill'] = 'yes'
        
        # identify INSIDE
        if heir[0][i][3] != -1:
            # we have a parent
            parent = heir[0][i][3]
            while not (parent in names):
                parent = heir[0][parent][3]
                if parent == -1:
                    break
            if parent != -1 and parent in names:
                obj['inside'] = names[parent]
        
        
        # identify ANGLE
        min_rect = cv2.minAreaRect(contour)
        angle = min_rect[2]
        if abs(angle) > 1.0:
            obj['angle'] = str(angle)
        
        
        name = chr(ord('Z') - obj_count) # generate a name, starting at Z and working backwards
        names[i] = name
        obj_count += 1
        fig[name] = obj
        rects[name] = rect
    
    # pprint(rects)
    
    # identify ABOVE and LEFT-OF
    if len(fig) > 2:
        rects_sorted_by_x = sorted(rects.items(), key=lambda r: r[1][0])
        rects_sorted_by_y = sorted(rects.items(), key=lambda r: r[1][1])
        
        
        for j in range(len(fig) - 1):
            name = rects_sorted_by_x[j][0]
            fig[name]['left-of'] = []
            for k in range(j + 1, len(fig)):
                next_name = rects_sorted_by_x[k][0]
                fig[name]['left-of'] += [next_name]
        
        for j in range(len(fig) - 1):
            name = rects_sorted_by_y[j][0]
            fig[name]['above'] = []
            for k in range(j + 1, len(fig)):
                next_name = rects_sorted_by_y[k][0]
                fig[name]['above'] += [next_name]
                
    #pprint(fig)
    #cv2.waitKey()
    return fig


def get_shape_name(n):
    if n == 3:
        return 'triangle'
    elif n == 4:
        return 'rectangle'
    elif n == 5:
        return 'pentagon'
    elif n == 6:
        return 'hexagon'
    elif n == 7:
        return 'septagon'
    elif n == 8:
        return 'octagon'
    else:
        return 'circle'


def pythonize(problem):
    """Returns a pythonic version of a problem object"""
    
    ret = {}
    ret['type'] = problem.getProblemType()
    ret['name'] = problem.getName()
    ret['figures'] = figures = {}
    
    for fig in problem.getFigures().values():
        path = fig.getPath()
        figures[fig.getName()] = visual_to_textual(path)
        # for obj in fig.getObjects():
        #     objs[obj.getName()] = attrs = {}
        #     for attr in obj.getAttributes():
        #         value = attr.getValue()
        #         values = [value]
        #         if ',' in value:
        #             values = value.split(',')
        #         attrs[attr.getName()] = values
    
    return ret