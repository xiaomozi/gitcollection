#


class FbxMeshReduce:
    def __init__(self,kwargs):
        option = kwargs
        self.nodes={}
        self.inputFbxFile = self._checkValue(option['inputFbxFile'])
        self.compressionRate = self._checkValue(option['compressionRate']) or 70 
        self.outputBaker = self._checkValue(option['outputBaker'])
        self.outputFbx = self._checkValue(option['outputFbx'])
        self.attachTexture = self._checkValue(option['attachTexture'])
        self.outputObj = self._checkValue(option['outputObj'])
        self.baker = self._checkValue(option['baker'])
        
        try:
            import hou
            
        except ImportError:
            
            print('import hou error')
        
        self.compress()
        
        pass


    def _checkValue(self,value):
        if value == "None":
            return None
        else:
            return value
        
    def _importFbx(self,attachTexture = None):
        try:
            
            f = hou.hipFile.importFBX(self.inputFbxFile)
            obj = f[0]
            
            geo,mat,*_ = obj.children()
            *_,material = geo.children()

            
            self.nodes['geo'] = geo
            self.nodes['material'] = material

            if not attachTexture:
                return
            attachMat,*_ = mat.children()
            if not attachMat.parm('basecolor_useTexture').eval():
                attachMat.parm('basecolor_useTexture').set(1)
                attachMat.parm('basecolor_texture').set(attachTexture)
            
            
        except Exception:
            #raise Exception('fail to import {0}'.format(self.inputFbxFile))
            print('fail to import {0}'.format(self.inputFbxFile))
        

    def _createNodes(self):
        geo  =  self.nodes['geo']
        polyreduce = geo.createNode('polyreduce::2.0','polyreduce2')
        uv = geo.createNode('uvlayout','uvlayout2')
        material2 = geo.createNode('material','material2')
        baker = geo.createNode('maps_baker','maps_baker1')
        
        #default baker:not baker
        compressSwitch  = geo.createNode('switch','switch2')
        
        fbxout = geo.createNode('rop_fbx','rop_fbx1')
        clean = geo.createNode('clean','clean1')
        fusePoly = geo.createNode('fuse','fuse2')

        normal  = geo.createNode('normal','normal2')
        clean3  = geo.createNode('clean','clean3')
        rop_geometry2  = geo.createNode('rop_geometry','rop_geometry2')

        self.nodes['polyreduce'] =polyreduce
        self.nodes['uv'] =uv
        self.nodes['material2'] =material2
        self.nodes['baker'] =baker
        self.nodes['compressSwitch']=compressSwitch
        self.nodes['fbxout'] =fbxout
        self.nodes['clean'] =clean
        self.nodes['fusePoly'] = fusePoly

        self.nodes['normal'] = normal
        self.nodes['clean3'] = clean3
        self.nodes['rop_geometry2'] = rop_geometry2

    def _connectNodes(self):

        self.nodes['uv'].setFirstInput(self.nodes['material'])
        self.nodes['material2'].setFirstInput(self.nodes['uv'])
        self.nodes['baker'].setFirstInput(self.nodes['uv'])
        self.nodes['baker'].setNextInput(self.nodes['material'])
        self.nodes['clean'].setFirstInput(self.nodes['baker'])
        
        self.nodes['compressSwitch'].setFirstInput(self.nodes['clean'])
        self.nodes['compressSwitch'].setNextInput(self.nodes['material'])

        self.nodes['fusePoly'].setFirstInput(self.nodes['compressSwitch'])
        self.nodes['polyreduce'].setFirstInput(self.nodes['fusePoly'])
        
        self.nodes['normal'].setFirstInput(self.nodes['polyreduce'])
        self.nodes['clean3'].setFirstInput(self.nodes['normal'])
        self.nodes['rop_geometry2'].setFirstInput(self.nodes['clean3'])

        self.nodes['fbxout'].setFirstInput(self.nodes['polyreduce'])
        pass

    def _setParameters(self):
        baker = self.nodes['baker']

        baker.parm('sOutputFile').set(self.outputBaker)
        baker.parm('bDiffuse').set(1)
        baker.parm('bVertexCd').set(0)
        baker.parm('bAO').set(0)
        #--------------------switch
        if self.baker:
           self.nodes['compressSwitch'].parm('input').set(1) 
        
        #--------------------
        polyreduce = self.nodes['polyreduce']
        polyreduce.parm('percentage').set(self.compressionRate)
        #-------------------
        self.nodes['clean3'].parm('dodelattribs').set(1)
        self.nodes['clean3'].parm('delattribs').set('* ^P ^uv')
        self.nodes['clean3'].parm('dodelgroups').set(1)
        #--------------------
        rop_geometry2 = self.nodes['rop_geometry2']
        rop_geometry2.parm('sopoutput').set(self.outputObj)
        #--------------------
        fbxout = self.nodes['fbxout']
        fbxout.parm('sopoutput').set(self.outputFbx)
        pass

    def _run(self):
        
        if self.outputBaker:
            print('baking {0}.......'.format(self.outputBaker))
            self.nodes['baker'].parm('execute').pressButton()
            
        if self.outputFbx:
            print('output Fbx file ...{0}'.format(self.outputFbx))
            self.nodes['fbxout'].parm('execute').pressButton()
            
        if self.outputObj:
            print('output OBJ file ...{0}'.format(self.outputObj))
            self.nodes['rop_geometry2'].parm('execute').pressButton()
        

    def compress(self):
        try:
            self._importFbx(self.attachTexture)
            self._createNodes()
            self._connectNodes()
            self._setParameters()
            self._run()
        except Exception :
            print('compress failed')
            #raise Exception("compress failed")
        

if __name__ == '__main__':
    
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--inputFbxFile", required=True,help="input Fbx filename")
    ap.add_argument("-o", "--outputFbx", required=False,help="output Fbx filename")
    ap.add_argument("-oj", "--outputJPEG", required=False,help="output baker filename")
    ap.add_argument("-r", "--compressionRate", required=True,help="reduction to the num of compressionRate")
    ap.add_argument("-a", "--attachTexture", required=False,help="attachTexture")
    ap.add_argument("-obj", "--outputObj", required=False,help="save files in OBJ fileformat")
    ap.add_argument("-ba", "--baker", required=False,help="baker")
    args = vars(ap.parse_args())
    
    inputFbxFile = args['inputFbxFile']
    compressionRate = args['compressionRate']
    outputBaker = args['outputJPEG']
    outputFbx = args['outputFbx']
    outputObj = args['outputObj']
    attachTexture = args['attachTexture']
    baker = args['baker']
    # options = {
    #     'inputFbxFile':r'F:\code\mygitcollection\houdini\cube.fbx',
    #     'compressionRate':20,
    #     'outputBaker':r'F:\code\mygitcollection\houdini\baker.jpg',
    #     'outputFbx':r'F:\code\mygitcollection\houdini\temp.fbx'
    # }
    options = {
        'inputFbxFile':r'{0}'.format(inputFbxFile),
        'compressionRate':compressionRate or int(compressionRate),
        'outputBaker':r'{0}'.format(outputBaker),
        'outputFbx':r'{0}'.format(outputFbx),
        'outputObj':r'{0}'.format(outputObj),
        'attachTexture':r'{0}'.format(attachTexture),
        'baker':r'{0}'.format(baker)
    }
    fbx = FbxMeshReduce(options)
