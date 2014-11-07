#
# Example for RBM (Restricted Boltzmann Machine) based model
#

def main(workspace, **kwargs):

    # create and optimize model
    model = workspace.model(
        name     = 'sim1-rbm',
        network  = 'example.3-layer',
        dataset  = 'example.sim1-binary',
        system   = 'ann.rbm',
        optimize = 'example.cd')

    # save model in projects directory
    workspace.saveModel(model)

    # create plot
    workspace.plot(model, 'ann.HiddenLayerGraph')
