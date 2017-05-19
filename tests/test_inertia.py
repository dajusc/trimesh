import generic as g


class InertiaTest(g.unittest.TestCase):

    def test_inertia(self):
        t0 = g.np.array([[-0.419575686853, -0.898655215203, -0.127965023308,  0. ],
                  [ 0.712589964872, -0.413418145015,  0.566834172697,  0. ],
                  [-0.562291548012,  0.146643245877,  0.813832890385,  0.],
                  [ 0.            ,  0.            ,  0.            ,  1. ]])
        t1 = g.np.array([[ 0.343159553585,  0.624765521319, -0.701362648103,  0.],
           [ 0.509982849005, -0.750986657709, -0.419447891476,  0.            ],
           [-0.788770571525, -0.213745370274, -0.57632794673 ,  0.            ],
           [ 0.            ,  0.            ,  0.            ,  1.            ]])
        
        # make sure our transformations are actually still transformations
        assert g.np.abs(g.np.dot(t0, t0.T) - g.np.eye(4)).max() < 1e-10
        assert g.np.abs(g.np.dot(t1, t1.T) - g.np.eye(4)).max() < 1e-10
        
        
        c = g.trimesh.primitives.Cylinder(height=10, 
                                        radius=1, 
                                        sections=720, # number of slices
                                        transform=t0)
        c0m = c.moment_inertia.copy()
        c0 = g.trimesh.inertia.cylinder_inertia(c.volume,
                              c.primitive.radius,
                              c.primitive.height,
                              c.primitive.transform)
                              
        ct = g.np.abs((c0m / c0) - 1) 
                              
        # we are comparing an inertia tensor from a mesh of a cylinder
        # to an inertia tensor from an actual cylinder, so allow for some 
        # discretization uncertainty
        assert ct.max() < 1e-3                      
                              
        # check our principal axis calculation against this cylinder
        # the direction (long axis) of the cylinder should correspond to
        # the smallest principal component of inertia, AKA rotation along
        # the axis, rather than the other two which are perpendicular
        components, vectors = g.trimesh.inertia.principal_axis(c.moment_inertia)
        axis_test = g.np.abs((vectors[components.argmin()] / c.direction) - 1)
        assert axis_test.max() < 1e-8

        # make sure Trimesh attribute is plumbed correctly
        base = c.principal_inertia
        assert g.np.allclose(base[0], components)
        assert g.np.allclose(base[1], vectors)
        
        
        # the other two axis of the cylinder should be identical
        assert g.np.abs(g.np.diff(g.np.sort(components)[-2:])).max() < 1e-8
        
        m = g.get_mesh('featuretype.STL')                      
        i0 = m.moment_inertia.copy()
        # rotate the moment of inertia
        i1 = g.trimesh.inertia.transform_inertia(transform=t0, inertia_tensor=i0)

        # rotate the mesh
        m.apply_transform(t0)
        # check to see if the rotated mesh + recomputed moment of inertia
        # is close to the rotated moment of inertia
        tf_test = g.np.abs((m.moment_inertia / i1) - 1)  
        assert tf_test.max() < 1e-6   
        
        # do it again with another transform
        i2 = g.trimesh.inertia.transform_inertia(transform=t1, inertia_tensor=i1)
        m.apply_transform(t1)
        tf_test = g.np.abs((m.moment_inertia / i2) - 1) 
        assert tf_test.max() < 1e-6  
        

if __name__ == '__main__':
    g.trimesh.util.attach_to_log()
    g.unittest.main()
