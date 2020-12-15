#


class FbxMeshReduce:
    def __init__(self,kwargs):
        option = kwargs
        self.nodes={}
        self.inputFbxFile = option['inputFbxFile']
        self.compressionRate = option['compressionRate'] or 70 
        self.outputBaker = option['outputBaker']
        self.outputFbx = option['outputFbx']
        self.attachTexture = option['attachTexture']
        
        try:
            import hou
            
        except ImportError:
            
            raise Exception('import hou error')
        
        self.compress()
        
        pass


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
            raise Exception('fail to import {0}'.format(self.inputFbxFile))
        

    def _createNodes(self):
        geo  =  self.nodes['geo']
        polyreduce = geo.createNode('polyreduce::2.0','polyreduce2')
        uv = geo.createNode('uvlayout','uvlayout2')
        material2 = geo.createNode('material','material2')
        baker = geo.createNode('maps_baker','maps_baker1')
        fbxout = geo.createNode('rop_fbx','rop_fbx1')
        clean = geo.createNode('clean','clean1')
        fusePoly = geo.createNode('fuse','fuse2')

        self.nodes['polyreduce'] =polyreduce
        self.nodes['uv'] =uv
        self.nodes['material2'] =material2
        self.nodes['baker'] =baker
        self.nodes['fbxout'] =fbxout
        self.nodes['clean'] =clean
        self.nodes['fusePoly'] = fusePoly

        pass

    def _connectNodes(self):

        self.nodes['uv'].setFirstInput(self.nodes['material'])
        self.nodes['material2'].setFirstInput(self.nodes['uv'])
        self.nodes['baker'].setFirstInput(self.nodes['uv'])
        self.nodes['baker'].setNextInput(self.nodes['material'])
        self.nodes['clean'].setFirstInput(self.nodes['baker'])
        self.nodes['fusePoly'].setFirstInput(self.nodes['clean'])
        self.nodes['polyreduce'].setFirstInput(self.nodes['fusePoly'])

        self.nodes['fbxout'].setFirstInput(self.nodes['polyreduce'])
        pass

    def _setParameters(self):
        baker = self.nodes['baker']

        baker.parm('sOutputFile').set(self.outputBaker)
        baker.parm('bDiffuse').set(1)
        baker.parm('bVertexCd').set(0)
        baker.parm('bAO').set(0)
        #--------------------
        polyreduce = self.nodes['polyreduce']
        polyreduce.parm('percentage').set(self.compressionRate)
        #--------------------
        fbxout = self.nodes['fbxout']
        fbxout.parm('sopoutput').set(self.outputFbx)
        pass

    def _run(self):
        self.nodes['baker'].parm('execute').pressButton()
        self.nodes['fbxout'].parm('execute').pressButton()
        pass

    def compress(self):
        try:
            self._importFbx(self.attachTexture)
            self._createNodes()
            self._connectNodes()
            self._setParameters()
            self._run()
        except Exception :
            print('compress failed')
            raise Exception("compress failed")
        

if __name__ == '__main__':
    
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--inputFbxFile", required=True,help="input Fbx filename")
    ap.add_argument("-o", "--outputFbx", required=True,help="output Fbx filename")
    ap.add_argument("-oj", "--outputJPEG", required=True,help="output baker filename")
    ap.add_argument("-r", "--compressionRate", required=True,help="reduction to the num of compressionRate")
    ap.add_argument("-a", "--attachTexture", required=False,help="attachTexture")
    args = vars(ap.parse_args())
        
    inputFbxFile = args['inputFbxFile']
    compressionRate = args['compressionRate']
    outputBaker = args['outputJPEG']
    outputFbx = args['outputFbx']
    attachTexture = args['attachTexture']
 
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
        'attachTexture':r'{0}'.format(attachTexture)
    }
    fbx = FbxMeshReduce(options)
