# -*- coding: utf-8 -*-
import nemoa

import xlwt

def report(self, model, file, **params):
    
    # check object class
    if not model.__class__.__name__ == 'mp_model':
        nemoa.log('error', "could not create table: 'model' has to be mp_model instance!")
        return False
    
    # set default settings
    settings = {
        'columns': ['knockout_approx']}
        
    # get empty file
    file = nemoa.common.getEmptyFile(file)

    # start document
    book = xlwt.Workbook(encoding="utf-8")

    # define common styles
    style_sheet_head = xlwt.Style.easyxf(
        'font: height 300;')
    style_section_head = xlwt.Style.easyxf('font: bold True;')
    style_head = xlwt.Style.easyxf(
        'pattern: pattern solid, fore_colour gray_ega;'
        'borders: bottom thin;'
        'font: colour white;')
    style_str = xlwt.Style.easyxf('', '')
    style_num = xlwt.Style.easyxf('alignment: horizontal left;', '#,###0.000')
    style_num_1 = xlwt.Style.easyxf('alignment: horizontal left;', '#,###0.0')
    style_num_2 = xlwt.Style.easyxf('alignment: horizontal left;', '#,###0.00')
    style_num_3 = xlwt.Style.easyxf('alignment: horizontal left;', '#,###0.000')
    style_border_left = xlwt.Style.easyxf('borders: left thin;')
    style_border_bottom = xlwt.Style.easyxf('borders: bottom thin;')

    sheet = {}
    
    #
    # EXCEL SHEET 'UNITS'
    #
    
    sheet['units'] = book.add_sheet("Units")
    row = 0
    
    # write sheet headline
    sheet['units'].row(row).height = 390
    sheet['units'].row(row).write(0, 'Units', style_sheet_head)
    row +=2
    
    # write section headline
    sheet['units'].row(row).write(0, 'Unit', style_section_head)
    sheet['units'].row(row).write(3, 'Data', style_section_head)
    sheet['units'].row(row).write(5, 'Parameter', style_section_head)
    sheet['units'].row(row).write(7, 'Effect', style_section_head)
    row += 1
    
    # write column headline
    columns = [ {
            'label': 'id', 'col': 0,
            'info': 'node_id', 'type': 'string', 'style': style_str
        }, {
            'label': 'class', 'col': 1,
            'info': 'node_type', 'type': 'string', 'style': style_str
        }, {
            'label': 'label', 'col': 2,
            'info': 'node_label', 'type': 'string', 'style': style_str
        }, {
            'label': 'mean', 'col': 3,
            'info': 'data_mean', 'type': 'number', 'style': style_num
        }, {
            'label': 'sdev', 'col': 4,
            'info': 'data_sdev', 'type': 'number', 'style': style_num
        }, {
            'label': 'bias', 'col': 5,
            'info': 'model_bias', 'type': 'number', 'style': style_num
        }, {
            'label': 'sdev', 'col': 6,
            'info': 'model_sdev', 'type': 'number', 'style': style_num
        }, {
            'label': 'rel approx [%]', 'col': 7,
            'info': 'model_rel_approx', 'type': 'number', 'style': style_num_1
        }, {
            'label': 'abs approx [%]', 'col': 8,
            'info': 'model_abs_approx', 'type': 'number', 'style': style_num_1
        }]
        
    if 'knockout_approx' in settings['columns']:
        columns.append({
            'label': 'knockout', 'col': 9,
            'info': 'model_knockout_approx', 'type': 'number', 'style': style_num_1
        })

    for cell in columns:
        sheet['units'].row(row).write(cell['col'], cell['label'], style_head)
    
    row += 1
    
    # write unit information
    nodes = model.network.nodes()
    
    # get simulation info
    model_rel_approx, node_rel_approx = model.get_approx(type = 'rel_approx')
    model_abs_approx, node_abs_approx = model.get_approx(type = 'abs_approx')
    
    if 'knockout_approx' in settings['columns']:
        node_knockout_approx = model.get_knockout_approx()

    for node in nodes:
        # create dict with info
        info = {}
        
        # get node information
        network_info = model.network.node(node)
        info['node_id'] = node
        info['node_type'] = network_info['params']['type']
        info['node_label'] = network_info['label']

        # get data and model information
        system_info = model.system.unit(node)
        if system_info['type'] == 'visible':
            info['data_mean'] = system_info['data']['mean']
            info['data_sdev'] = system_info['data']['sdev']
            info['model_bias'] = system_info['params']['bias']
            info['model_sdev'] = system_info['params']['sdev']
            info['model_rel_approx'] = node_rel_approx[node] * 100
            info['model_abs_approx'] = node_abs_approx[node] * 100
        else:
            info['model_bias'] = system_info['params']['bias']
            
        if 'knockout_approx' in settings['columns']:
            info['model_knockout_approx'] = node_knockout_approx[node] * 100
            
        # write cell content
        for cell in columns:
            if not cell['info'] in info:
                continue
            
            if cell['type'] == 'string':
                sheet['units'].row(row).write(
                    cell['col'], info[cell['info']], cell['style'])
            elif cell['type'] == 'number':
                sheet['units'].row(row).set_cell_number(
                    cell['col'], info[cell['info']], cell['style'])
                    
        row += 1

    #
    # EXCEL SHEET 'LINKS'
    #
    
    sheet['links'] = book.add_sheet("Links")
    row = 0
    
    # write sheet headline
    sheet['links'].row(row).height = 390
    sheet['links'].row(row).write(0, 'Links', style_sheet_head)
    row +=2
    
    # write section headline
    sheet['links'].row(row).write(0, 'Source', style_section_head)
    sheet['links'].row(row).write(3, 'Target', style_section_head)
    sheet['links'].row(row).write(6, 'Parameter', style_section_head)
    sheet['links'].row(row).write(7, 'Effect', style_section_head)
    row += 1
        
    # write column headline
    columns = [ {
            'label': 'id', 'col': 0,
            'info': 'src_node_id', 'type': 'string', 'style': style_str
        }, {
            'label': 'class', 'col': 1,
            'info': 'src_node_type', 'type': 'string', 'style': style_str
        }, {
            'label': 'label', 'col': 2,
            'info': 'src_node_label', 'type': 'string', 'style': style_str
        },{
            'label': 'id', 'col': 3,
            'info': 'tgt_node_id', 'type': 'string', 'style': style_str
        }, {
            'label': 'class', 'col': 4,
            'info': 'tgt_node_type', 'type': 'string', 'style': style_str
        }, {
            'label': 'label', 'col': 5,
            'info': 'tgt_node_label', 'type': 'string', 'style': style_str
        }, {
            'label': 'weight', 'col': 6,
            'info': 'weight', 'type': 'number', 'style': style_num
        }, {
            'label': 'energy', 'col': 7,
            'info': 'energy', 'type': 'number', 'style': style_num
        } ]
        
    for cell in columns:
        sheet['links'].row(row).write(cell['col'], cell['label'], style_head)
    
    row += 1
    
    # write link information
    edges = model.network.edges()
    
    # link knockout simulation
    edge_energy = model.get_weights(type = 'linkenergy')
    
    for (src_node, tgt_node) in edges:
        
        # create dict with info
        info = {}
        
        # get source node information
        network_info_src = model.network.node(src_node)
        info['src_node_id'] = src_node
        info['src_node_type'] = network_info_src['params']['type']
        info['src_node_label'] = network_info_src['label']
        
        # get target node information
        network_info_tgt = model.network.node(tgt_node)
        info['tgt_node_id'] = tgt_node
        info['tgt_node_type'] = network_info_tgt['params']['type']
        info['tgt_node_label'] = network_info_tgt['label']
        
        # simulation
        info['energy'] =  edge_energy[(src_node, tgt_node)]
        
        # get data and model information
        system_info = model.system.link((src_node, tgt_node))
        
        if not system_info == {}:
            info['weight'] = system_info['params']['weight']
        
        # write cell content
        for cell in columns:
            if not cell['info'] in info:
                continue
            
            if cell['type'] == 'string':
                sheet['links'].row(row).write(
                    cell['col'], info[cell['info']], cell['style'])
            elif cell['type'] == 'number':
                sheet['links'].row(row).set_cell_number(
                    cell['col'], info[cell['info']], cell['style'])
                    
        row += 1
        
    book.save(file)
    
    return True
