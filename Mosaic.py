from numpy import iterable,r_,cumsum
from matplotlib.colors import rgb_to_hsv, hsv_to_rgb
from collections import Counter, OrderedDict
import numpy as np
import matplotlib.pyplot as plt

single_rgb_to_hsv=lambda rgb: rgb_to_hsv( np.array(rgb).reshape(1,1,3) ).reshape(3)
single_hsv_to_rgb=lambda hsv: hsv_to_rgb( np.array(hsv).reshape(1,1,3) ).reshape(3)

def split_rect(point,width,height,proportion,direction='horizontal',gap=0.05):
    """
    divide un rettangolo in n pezzi secondo una proporzione data
    """
    x,y = point
    direction = direction[0]
    proportion = proportion if iterable(proportion) else array([proportion,1.-proportion])
    if sum(proportion)<1:
        proportion = r_[proportion,1.-sum(proportion)]
    left = r_[0,cumsum(proportion)]
    left /= left[-1]*1.
    L = len(left)
    gap_w = gap#*width
    gap_h = gap#*height
    size = 1. + gap*(L-2)
    #size=1.
    if  direction == 'h':
        #return [ ((x,y+height*left[idx]+gap_h*(0<idx<L-1)),width,height*proportion[idx]-gap_h-gap_h*(0<idx<L-2)) for idx in range(L-1)]
        sol = []
        for idx in range(L-1):
            new_y = y+(height*left[idx]+gap_h*idx)/size
            new_h = height*proportion[idx]/size
            sol.append(((x,new_y),width,new_h))
        return sol
        #return [ ((x,(y+height*left[idx]+gap_h*idx)/size),width,height*proportion[idx]) for idx in range(L-1)]
    elif direction == 'v':
        #return [ ((x+width*left[idx]+gap_w*(0<idx<L-1),y),width*proportion[idx]-gap_w-gap_w*(0<idx<L-2),height) for idx in range(L-1)]
        sol = []
        for idx in range(L-1):
            new_x = x+(width*left[idx]+gap_w*idx)/size
            new_w = width*proportion[idx]/size
            sol.append(((new_x,y),new_w,height))
        return sol
        #return [ (((x+width*left[idx]+gap_w*idx)/size,y),width*proportion[idx],height) for idx in range(L-1)]
    else:
        raise ValueError("direction of division should be 'vertical' or 'horizontal'")
        


def MosaicDivision(counted,direction='v',gap=0.005):
    """
    given a dictionary of counting for each category, it return the Rectangles
    Bounding boxes and the relative axis ticks
    """
    #preparazione dei valori da utilizzare
    ticks_tot = []
    rects2 = { ('total',):((0,0),1,1) }
    
    #categories = [ list(OrderedSet(i)) for i in zip(*(counted.keys())) ]
    #uso l'orderedDict come un orderedSet
    categories = [ list(OrderedDict([(j,None) for j in i])) for i in zip(*(counted.keys())) ]
    
    #inizio il ciclo per le varie categorie
    #divido ricorsivamente i vari rettangoli

    def recursive_split(rect_key,rect_coords,category_idx,split_dir,gap):
        """
        given a key of the boxes and the data to analyze,
        split the key into several keys stratificated by the given
        category in the assigned direction
        """
        ticks = []
        category = categories[category_idx]
        chiave=rect_key
        divisione = OrderedDict()
        for tipo in category:
            divisione[tipo]=0.
            for k,v in counted.items():
                if k[len(rect_key)-1]!=tipo:
                    continue 
                if not all( k[k1]==v1 for k1,v1 in enumerate(rect_key[1:])):
                    continue
                divisione[tipo]+=v
        totali = 1.*sum(divisione.values())
        if totali: #check for empty categories
            divisione = OrderedDict( (k,v/totali) for k,v in divisione.items() )
        else:
            divisione = OrderedDict( (k,0.) for k,v in divisione.items() )
        prop = divisione.values()
        div_keys = divisione.keys()
        new_rects = split_rect(*rect_coords,proportion=prop,direction=split_dir,gap=gap)
        divisi = OrderedDict( (chiave+(k,),v) for k,v in zip(div_keys,new_rects))
        d = (split_dir == 'h')
        ticks = [ (k,O[d]+0.5*[h,w][d]) for k,(O,h,w) in zip(div_keys,new_rects) ]
        return divisi,zip(*ticks)
   
    for cat in range(len(categories)):
        tipi = categories[cat]
        chiavi = rects2.keys()
        res = OrderedDict()
        #per ogni categoria pesco le chiavi dal dizionario dei rettangoli
        #le divido in base alle categorie presenti e le reinserisco
        # in un nuovo dizionario
        temp_ticks = []
        for chiave,coords in rects2.items():
            
            partial,ticks = recursive_split(chiave,coords,cat,direction,gap/2.**cat)
            res.update(partial)
            temp_ticks.append(ticks)
            #if len(ticks_tot)<=cat:
            #    ticks_tot.append(ticks)
        ticks_tot.append(temp_ticks[0 if cat<2 else -1])
        rects2=res
        direction = 'h' if direction=='v' else 'v'
        #level+=1
        
    rects2 = { k[1:]:v for k,v in rects2.items() }
    return rects2,ticks_tot,categories



def MosaicPlot(data,ax=None,direction='v',gap=0.005,decorator=None):
    """
    it create the actual plot:
        takes the set of boxes of the division with the ticks
        use the decorator to generate the patches
        draw the patches
        draw the appropriate ticks on the plot
    """
    if ax is None:
        ax=plt.gca()
    data = OrderedDict( (k,v) for k,v in sorted(data.items()) )
    rects,ticks,categories = MosaicDivision(data,direction=direction,gap=gap)

    if decorator is None:
        L = [1.*len(cat) for cat in categories]
        props = [ np.linspace(0,1,l+2)[1:-1] for l in L ]
        if len(L)==4:
            props[3]=[ '', 'x', '/', '\\', '|', '-', '+',  'o', 'O', '.', '*' ]
        def dec(cat):
            prop = [ props[k][categories[k].index(cat[k])] for k in range(len(cat)) ]
            hsv = [0., 0.4, 0.7]
            for idx,i in enumerate(prop[:3]):
                hsv[idx]=i
            hatch = prop[3] if len(prop)==4 else ''
            return dict( color=single_hsv_to_rgb(hsv), hatch=hatch )
        decorator = dec
    ax.set_xticks([])
    ax.set_xticklabels([])
    ax.set_yticks([])
    ax.set_yticklabels([])
    
    for k,r in rects.items():
        ax.add_patch(plt.Rectangle(*r,**(decorator(k))))
    
    for idx,t in enumerate(ticks):
        for (lab,pos) in zip(*t):
            s = 0.02
            border= -s if idx<2 else 1+s
            valign= 'top' if idx<2 else 'baseline'
            halign= 'right' if idx<2 else 'left'
            x,y,v,h = (border,pos,'center',halign) if (direction =='v')!=(not idx%2) else (pos,border,valign,'center')
            size = ['xx-large','x-large','large','large','medium','medium','small','x-small'][idx]
            ax.text(x,y,lab,horizontalalignment = h, verticalalignment = v,size=size,rotation=0)