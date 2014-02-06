/* -*- coding: utf-8 -*- 
*
* Copyright Institut de Recherche et d'Innovation © 2014
*
* contact@iri.centrepompidou.fr
*
* Ce code a été développé pour un premier usage dans JocondeLab, projet du 
* ministère de la culture et de la communication visant à expérimenter la
* recherche sémantique dans la base Joconde
* (http://jocondelab.iri-research.org/).
*
* Ce logiciel est régi par la licence CeCILL-C soumise au droit français et
* respectant les principes de diffusion des logiciels libres. Vous pouvez
* utiliser, modifier et/ou redistribuer ce programme sous les conditions
* de la licence CeCILL-C telle que diffusée par le CEA, le CNRS et l'INRIA 
* sur le site "http://www.cecill.info".
*
* En contrepartie de l'accessibilité au code source et des droits de copie,
* de modification et de redistribution accordés par cette licence, il n'est
* offert aux utilisateurs qu'une garantie limitée.  Pour les mêmes raisons,
* seule une responsabilité restreinte pèse sur l'auteur du programme,  le
* titulaire des droits patrimoniaux et les concédants successifs.
*
* A cet égard  l'attention de l'utilisateur est attirée sur les risques
* associés au chargement,  à l'utilisation,  à la modification et/ou au
* développement et à la reproduction du logiciel par l'utilisateur étant 
* donné sa spécificité de logiciel libre, qui peut le rendre complexe à 
* manipuler et qui le réserve donc à des développeurs et des professionnels
* avertis possédant  des  connaissances  informatiques approfondies.  Les
* utilisateurs sont donc invités à charger  et  tester  l'adéquation  du
* logiciel à leurs besoins dans des conditions permettant d'assurer la
* sécurité de leurs systèmes et ou de leurs données et, plus généralement, 
* à l'utiliser et l'exploiter dans les mêmes conditions de sécurité. 
*
* Le fait que vous puissiez accéder à cet en-tête signifie que vous avez 
* pris connaissance de la licence CeCILL-C, et que vous en avez accepté les
* termes.
*
*/

$(function() {
    var map = L.map('map', {
        center: [20, 0],
        zoom: 2,
        maxBounds: [[-100,-200],[100,200]]
    });
    window.lmap = map;
    L.tileLayer(
        "http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        {
            attribution: gettext("© contributeurs de OpenStreetMap")
        }
    ).addTo(map);
    L.Icon.Default.imagePath = urls.icons_default_image_path;
    var coordCache = [],
        coordIdCache = [],
        defaultIcon = new L.Icon.Default(),
        orangeIcon = new L.Icon.Default({iconUrl: urls.orange_marker }),
        lightIcon =  new L.Icon.Default({iconUrl: urls.light_marker }),
        country_uris = _(countries).pluck("dbpedia_uri"),
        itemCount = 12,
        scaleBase = Math.log(countries[0].nb_notices),
        currentCountry = null,
        hideCountryTimeout = false,
        preHideTimeout = false,
        mapDragging = false,
        oms = new OverlappingMarkerSpiderfier(map),
        $map = $("#map");
    
    function getData() {
        var bounds = map.getBounds();
        $.getJSON(
            urls.ajax_geo_coords,
            {
                min_lat: bounds.getSouth(),
                max_lat: bounds.getNorth(),
                min_lng: bounds.getWest(),
                max_lng: bounds.getEast()
            },
            function(data) {
                _(data).each(function(coord) {
                    if (coordIdCache.indexOf(coord.dbpedia_uri) === -1 && country_uris.indexOf(coord.dbpedia_uri) === -1) {
                        coordIdCache.push(coord.dbpedia_uri);
                        coordCache.push(coord);
                    }
                });
                coordCache = _(coordCache).sortBy(function(coord) {
                    return -coord.sum_notices;
                });
                showData();
            }
        );
        showData();
    }
    
    function selectFeature(dbpedia_uri, blockHistory) {
        _(coordCache).each(function(coord) {
            if (coord.dbpedia_uri === dbpedia_uri) {
                coord.isCurrent = true;
                showCoord(coord);
                coord.marker.setIcon(orangeIcon);
                map.setView([coord.latitude, coord.longitude], Math.max(Math.min(12,map.getZoom() + 1),6));
                showCoord(coord);
            } else {
                coord.isCurrent = false;
                if (coord.marker) {
                    coord.marker.setIcon(defaultIcon);
                }
            }
        });
        _(countries).each(function(c) {
            if (c.dbpedia_uri === dbpedia_uri) {
                c.layer.setStyle({weight: 5, color: "#c00000", opacity: .8});
                map.fitBounds(c.bounds);
            } else {
                if (c.layer) {
                    c.layer.setStyle({weight: 1, color: "#000080", opacity: .3});
                }
            }
        });
        loadSearchResults({ dbpedia_uri: dbpedia_uri, thesaurus:'LIEUX' });
        if (!blockHistory) {
            window.history.pushState("","","#"+encodeURIComponent(dbpedia_uri));
        }
    }
        
    function showDbpedia(feature) {
        clearCountryTimeout();
        if (!feature) {
            dbpediaBox.hide();
            return;
        }
        var fb = feature.bounds,
            mb = map.getBounds();
        if (fb) {
            if (!mb.intersects(fb)) {
                hideDbpedia();
                return;
                }
            var c = L.latLngBounds(
                [Math.max(mb.getSouth(),fb.getSouth()), Math.max(mb.getWest(),fb.getWest())],
                [Math.min(mb.getNorth(),fb.getNorth()), Math.min(mb.getEast(),fb.getEast())]
            ).getCenter();
        } else {
            var c = feature.latlng;
        }
        if (!mb.contains(c)) {
            hideDbpedia();
            return;
        }
        var p = map.latLngToContainerPoint(c),
            mo = $map.offset(),
            y = p.y + mo.top;
        
        dbpediaBox.show(feature.dbpedia_uri);
        dbpediaBox.setAnchor({
            type: "box",
            box: { top: y - (fb ? 0 : 30), left: p.x + mo.left, bottom: y },
            positioning: "bottom"});
        dbpediaBox.recentre();
    }
    
    function hideDbpedia() {
        dbpediaBox.setAnchor();
        dbpediaBox.hide();
    }

    function setCountryTimeout() {
        hideCountryTimeout = setTimeout(function() {
            dbpediaBox.hide();
        }, 1000);
    }
    
    function clearCountryTimeout() {
        if (preHideTimeout) {
            clearTimeout(preHideTimeout);
            preHideTimeout = false;
        }
        if (hideCountryTimeout) {
            clearTimeout(hideCountryTimeout);
            hideCountryTimeout = false;
        }
    }    
    
    function showCoord(coord) {
        if (!coord.marker) {
            coord.latlng = L.latLng(coord.latitude, coord.longitude);
            var mk = coord.marker = L.marker(coord.latlng);
            map.addLayer(mk);
            oms.addMarker(mk);
            mk.coord = coord;
            mk.on("mouseover", function(marker) {
                if (!mapDragging) {
                    showDbpedia(coord);
                }
            });
            mk.on("mouseout", hideDbpedia);
        }
    }
    
    function showData() {
        var n = 0,
            bounds = map.getBounds(),
            nsew = {
                w: bounds.getWest(),
                e: bounds.getEast(),
                n: bounds.getNorth(),
                s: bounds.getSouth()
            };
        _(coordCache).each(function(coord) {
            if (coord.isCurrent || (n < itemCount && coord.latitude > nsew.s && coord.latitude < nsew.n && coord.longitude > nsew.w && coord.longitude < nsew.e) ) {
                n++;
                showCoord(coord);
            } else {
                if (coord.marker) {
                    oms.removeMarker(coord.marker);
                    map.removeLayer(coord.marker);
                    coord.marker = null;
                }
            }
        });
    }
    
    var gjs = L.geoJson(null, {
        style: function(f) {
            f.dbCountry = _(countries).find(function(c) { return c.iso_code_3 === f.id; });
            var styleobj = { weight: 1, color: "#000080", opacity: .3 };
            if (f.dbCountry && f.dbCountry.nb_notices) {
                var x = Math.min(1, Math.max(0, Math.log(f.dbCountry.nb_notices) / scaleBase)),
                    g = Math.floor(255*(1-.5*x)),
                    b = Math.floor(255*(1-x));
                styleobj.fillColor = "rgb(" + [255,g,b].join(",") + ")";
                styleobj.fillOpacity = .5;
            } else {
                styleobj.fillColor = "#000080";
                styleobj.fillOpacity = .2;
            }
            return styleobj;
        },
        onEachFeature: function(f, l) {
            if (f.dbCountry) {
                f.dbCountry.bounds = l.getBounds();
                f.dbCountry.latlng = f.dbCountry.bounds.getCenter();
                f.dbCountry.layer = l;
                l.on("click", function() { selectFeature(f.dbCountry.dbpedia_uri); });
                l.on("mouseover", function() {
                    if (!mapDragging && f.dbCountry !== currentCountry) {
                        showDbpedia(f.dbCountry);
                        currentCountry = f.dbCountry;
                        clearCountryTimeout();
                        preHideTimeout = setTimeout(function() {
                            l.once("mousemove", function() {
                                if (currentCountry === f.dbCountry && !hideCountryTimeout) {
                                    setCountryTimeout();
                                }
                            });
                        }, 1000);
                    }
                });
                l.on("mouseout", hideDbpedia);
            } else {
                l.on("mouseover", function() {
                    currentCountry = false;
                });
            }
        }
    });
    
    gjs.addTo(map);
        
    $.getJSON(urls.countries_geo_json, function(data) {
        gjs.addData(data);
    });
    
    $(window).on("popstate", function() {
        var h = document.location.hash.replace(/^#/,'');
        if (/https?:\/\//.test(h)) {
            selectFeature(h, true);
        } else {
            _(coordCache).each(function(coord) {
                coord.isCurrent = false;
                if (coord.marker) {
                    coord.marker.setIcon(defaultIcon);
                }
            });
            _(countries).each(function(c) {
                if (c.layer) {
                    c.layer.setStyle({weight: 1, color: "#000080", opacity: .3});
                }
            });
            $(".results").empty();
            map.setView([20, 0],2);
        }
    });
    
    var h = document.location.hash.replace(/^#/,'');
    if (/https?:\/\//.test(h)) {
        loadSearchResults({dbpedia_uri: h, thesaurus:'LIEUX'});
    }
        
    var debouncedGetData = _.debounce(getData,1000);
     
    debouncedGetData();
    
    map.on("movestart", function() {
        hideDbpedia();
    });
    map.on("moveend", function() {
        debouncedGetData();
        
    });
    oms.addListener("click", function(marker) {
        if (marker.coord) {
            selectFeature(marker.coord.dbpedia_uri);
        }
    });
    oms.addListener('spiderfy', function(markers) {
        _(markers).each(function(marker) {
            marker.setIcon(lightIcon);
        });
    });
    oms.addListener('unspiderfy', function(markers) {
        _(markers).each(function(marker) {
            marker.setIcon(defaultIcon);
        });
    });
    
    $(".dbpedia-overlay").mouseover(clearCountryTimeout);
    
    var blockUnsticking = false;
    
    $(".map-search-input").autocomplete({
        source: urls.ajax_geo_search,
        select: function(event, ui) {
            var coord = ui.item,
                countryindex = country_uris.indexOf(coord.dbpedia_uri);
            if (countryindex === -1) {
                if (coordIdCache.indexOf(coord.dbpedia_uri) === -1) {
                    coordIdCache.push(coord.dbpedia_uri);
                    coordCache.push(coord);
                    coordCache = _(coordCache).sortBy(function(coord) {
                        return -coord.sum_notices;
                    });
                    var feature = coord;
                } else {
                    var feature = _(coordCache).find(function(c) { return c.dbpedia_uri === coord.dbpedia_uri; });
                }
            }
            selectFeature(coord.dbpedia_uri);
            blockUnsticking = true;
            window.setTimeout(function() { blockUnsticking = false;}, 0);
        }
    });
    
    $(document).click(function() {
        if (!blockUnsticking) {
            stickyFeature = null;
        }
    });
});
