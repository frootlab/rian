#
# Example for DBN (Deep Beliefe Network) based model
#

def main(workspace, **kwargs):

    # create and optimize model
    model = workspace.model(
        name     = 'dbn',
        network  = 'example.5-layer',
        dataset  = 'example.sim1',
        system   = 'dbn.dbn',
        optimize = 'example.cd')

    # save model in projects directory
    #model.save()

    # create plot
    #model.plot('rbm.HiddenLayerGraph')
    #model.plot('rbm.InteractionHeatmap')
    #model.plot('rbm.DirectionHeatmap')
    #model.plot('rbm.ConnectionHeatmap')
