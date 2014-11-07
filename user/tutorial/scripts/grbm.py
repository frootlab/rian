#
# Example for GRBM (Gaussian Restricted Boltzmann Machine) based model
#

def main(workspace, **kwargs):

    # create and optimize model
    model = workspace.model(
        name     = 'grbm',
        network  = 'example.3-layer',
        dataset  = 'example.sim1',
        system   = 'rbm.grbm',
        optimize = 'example.cd')

    # save model in projects directory
    model.save()

    # create plot
    model.plot('rbm.HiddenLayerGraph')
    model.plot('rbm.InteractionHeatmap')
    model.plot('rbm.DirectionHeatmap')
    model.plot('rbm.ConnectionHeatmap')
