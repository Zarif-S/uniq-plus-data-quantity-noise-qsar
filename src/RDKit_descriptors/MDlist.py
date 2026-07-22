#rdMD RDKIT Descriptors from - https://github.com/molecularinformatics/Computational-ADME/blob/main/ML/ADME_ML_public.py
MDlist = []
try:
    MDlist.append(rdMolDescriptors.CalcTPSA(mol))
    MDlist.append(rdMolDescriptors.CalcFractionCSP3(mol))
    MDlist.append(rdMolDescriptors.CalcNumAliphaticCarbocycles(mol))
    MDlist.append(rdMolDescriptors.CalcNumAliphaticHeterocycles(mol))
    MDlist.append(rdMolDescriptors.CalcNumAliphaticRings(mol))
    MDlist.append(rdMolDescriptors.CalcNumAmideBonds(mol))
    MDlist.append(rdMolDescriptors.CalcNumAromaticCarbocycles(mol))
    MDlist.append(rdMolDescriptors.CalcNumAromaticHeterocycles(mol))
    MDlist.append(rdMolDescriptors.CalcNumAromaticRings(mol))
    MDlist.append(rdMolDescriptors.CalcNumLipinskiHBA(mol))
    MDlist.append(rdMolDescriptors.CalcNumLipinskiHBD(mol))            
    MDlist.append(rdMolDescriptors.CalcNumHeteroatoms(mol))
    MDlist.append(rdMolDescriptors.CalcNumRings(mol))
    MDlist.append(rdMolDescriptors.CalcNumRotatableBonds(mol))
    MDlist.append(rdMolDescriptors.CalcNumSaturatedCarbocycles(mol))
    MDlist.append(rdMolDescriptors.CalcNumSaturatedHeterocycles(mol))
    MDlist.append(rdMolDescriptors.CalcNumSaturatedRings(mol))
    MDlist.append(rdMolDescriptors.CalcHallKierAlpha(mol))
    MDlist.append(rdMolDescriptors.CalcKappa1(mol))
    MDlist.append(rdMolDescriptors.CalcKappa2(mol))
    MDlist.append(rdMolDescriptors.CalcKappa3(mol))
    MDlist.append(rdMolDescriptors.CalcChi0n(mol))
    MDlist.append(rdMolDescriptors.CalcChi0v(mol))
    MDlist.append(rdMolDescriptors.CalcChi1n(mol))
    MDlist.append(rdMolDescriptors.CalcChi1v(mol))
    MDlist.append(rdMolDescriptors.CalcChi2n(mol))
    MDlist.append(rdMolDescriptors.CalcChi2v(mol))
    MDlist.append(rdMolDescriptors.CalcChi3n(mol))
    MDlist.append(rdMolDescriptors.CalcChi3v(mol))
    MDlist.append(rdMolDescriptors.CalcChi4n(mol))
    MDlist.append(rdMolDescriptors.CalcChi4v(mol))
    MDlist.append(rdMolDescriptors.CalcAsphericity(mol))
    MDlist.append(rdMolDescriptors.CalcEccentricity(mol))   
    MDlist.append(rdMolDescriptors.CalcInertialShapeFactor(mol))
    MDlist.append(rdMolDescriptors.CalcExactMolWt(mol))  
    MDlist.append(rdMolDescriptors.CalcPBF(mol))  
    MDlist.append(rdMolDescriptors.CalcPMI1(mol))
    MDlist.append(rdMolDescriptors.CalcPMI2(mol))
    MDlist.append(rdMolDescriptors.CalcPMI3(mol))
    MDlist.append(rdMolDescriptors.CalcRadiusOfGyration(mol))
    MDlist.append(rdMolDescriptors.CalcSpherocityIndex(mol))
    MDlist.append(rdMolDescriptors.CalcLabuteASA(mol))
    MDlist.append(rdMolDescriptors.CalcNPR1(mol))
    MDlist.append(rdMolDescriptors.CalcNPR2(mol))
    for d in rdMolDescriptors.PEOE_VSA_(mol): 
        MDlist.append(d)
    for d in rdMolDescriptors.SMR_VSA_(mol): 
        MDlist.append(d)
    for d in rdMolDescriptors.SlogP_VSA_(mol): 
        MDlist.append(d)
    for d in rdMolDescriptors.MQNs_(mol): 
        MDlist.append(d)
    for d in rdMolDescriptors.CalcCrippenDescriptors(mol):
        MDlist.append(d)
    for d in rdMolDescriptors.CalcAUTOCORR2D(mol):  
        MDlist.append(d)
except:
    print ("The RDdescritpor calculation failed!")

rdMD[molName] = MDlist


'''Might need the below too,:

rdMD = {}
name_list = []

i=1
for mol in sdFile:
    if mol is not None:
        mol = standardize(mol)
        try:
            molName = mol.GetProp('_Name')
        except:
            try:
                molName = mol.GetProp('Vendor ID')
            except:
                molName = 'Molecule_%s' %i
        name_list.append(molName)
        try:
            activity = mol.GetProp('%s' % ADME_tag)
        except KeyError:
            activity = '0.0000'  
        act[molName] = float(activity)
        



'''