import argparse
import ijson.backends.yajl2_cffi as ijson
import bz2
from graph_tool.all import *

parser = argparse.ArgumentParser(description='Transform a Wikidata JSON Dump to a GraphTool Binary Graph.')
parser.add_argument('--dump', '-d', default="data/wikidata-20180813-all.json.bz2", help='the wikidata dump to load (wikidata-*-all.json.bz2)')
args = parser.parse_args()

wikidataFile = args.dump
universeFile = wikidataFile + '.universe.gt.bz2'
universeNoattrFile = wikidataFile + '.universe_noattr.gt.bz2'

def createGraph(amount = 30):

    items = ijson.items(bz2.open(wikidataFile, mode = 'rb'), 'item')

    count = 0
    universe = Graph()

    #dicts for o(1) lookup
    vertices = {}
    vertices['item'] = {}
    vertices['property'] = {}

    item = universe.new_vertex_property("bool") #type True=>item, False=>property
    q = universe.new_vertex_property("int") #items
    attributes = universe.new_vertex_property("object") #attributes
    label = universe.new_vertex_property("string") #labels
    aliases = universe.new_vertex_property("vector<string>") #aliases
    sitelinks = universe.new_vertex_property("int") #sitelinks
    enwiki = universe.new_vertex_property("string") #sitelinks
    p = universe.new_edge_property("int") #edge property

    try:
        for i in items:
            count += 1
            if (i['type'] == 'item') or (i['type'] == 'property'):

                # create node by item id
                node = int(i['id'][1:])

                if node in vertices[i['type']]:
                    n = vertices[i['type']][node]
                else:
                    n = vertices[i['type']][node] = universe.add_vertex()
                    q[n] = node


                # boolean for distinguishing to properties
                item[n] = (i['type'] == 'item')

                # claims
                attr = []

                if 'claims' in i:
                    for c in i['claims']:
                        for s in i['claims'][c]:
                            if 'qualifiers' in s and 'P582' in s['qualifiers']: # ignore claims which are not anymore valid (have a end qualifier)
                                break

                            if 'datatype' in s['mainsnak']:

                                if s['mainsnak']['datatype'] == 'wikibase-item' and  s['mainsnak']['snaktype'] == 'value': # it is a link
                                    value = s['mainsnak']['datavalue']['value']['numeric-id'] #integer
                                    if value in vertices[i['type']]:
                                        v = vertices[i['type']][value]
                                    else:
                                        v = vertices[i['type']][value] = universe.add_vertex()
                                        q[v] = value

                                    e = universe.add_edge(n,v)
                                    p[e] = int(s['mainsnak']['property'][1:])

                                else: # we have a string
                                    if s['mainsnak']['datatype'] == 'monolingualtext':
                                        if 'datavalue' in s['mainsnak'] and s['mainsnak']['datavalue']['value']['language'] == 'en':
                                            attr.append(s['mainsnak'])
                                    else:
                                        attr.append(s['mainsnak'])

                attributes[n] = attr

                # label
                if 'labels' in i:
                    if 'en' in i['labels']:
                        label[n] = i['labels']['en']['value']

                # aliases
                alss = []
                if 'aliases' in i:
                    if 'en' in i['aliases']:
                        for a in i['aliases']['en']:
                            alss.append(a['value'])
                aliases[n] = alss

                # sitelinks
                sl = 0
                if 'sitelinks' in i:
                    sl = len(i['sitelinks'])

                    if 'enwiki' in i['sitelinks'] and 'title' in i['sitelinks']['enwiki']:
                        enwiki[n] = i['sitelinks']['enwiki']['title']
                sitelinks[n] = sl

            if (not count % 1e3):
                print ("@ "+ "%.2e" % count + " with Node Q" + str(node))

            if(count == amount):
                break


    except KeyboardInterrupt:
        pass

    print ("Stopped after "+ "%.2e" % amount + " at Node Q" + str(node))

    universe.vertex_properties["item"] = item
    universe.vertex_properties["q"] = q
    universe.vertex_properties["attributes"] = attributes
    universe.vertex_properties["sitelinks"] = sitelinks
    universe.vertex_properties["enwiki"] = enwiki
    universe.vertex_properties["aliases"] = aliases
    universe.vertex_properties["label"] = label
    universe.edge_properties["p"] = p
    return universe

universe = createGraph(1e+100)
universe.save(universeFile)
print("Graph saved:", universeFile)
del universe.vertex_properties["attributes"]
universe.save(universeNoattrFile)
print("Graph saved:", universeNoattrFile)
