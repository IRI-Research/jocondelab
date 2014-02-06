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

/*
 Front Search
 * */

$(function() {
    
    bindResultsMouseover();
    if (typeof queryobj === "object" && queryobj) {
        scrollLoad(queryobj);
    }
    $(".update-ids").click(function(e){
    	var visited_ids = $("#visited_ids").val();
    	if(visited_ids==""){
    		$("#visited_ids").val(parseInt($(this).attr("data-id")));
    	}
    	else{
    		$("#visited_ids").val( visited_ids + "," + $(this).attr("data-id") );
    	}
    });
    
    var visited_ids = $("#visited_ids").val().split(',');
    $.each($(".notice-image"), function(i, e){
    	var im = $(e);
    	var a_par = im.parent();
    	if(visited_ids.indexOf(a_par.attr("data-id"))>=0){
    		im.addClass("visited");
    	}
    });
    
    // Check if a dom element is the current viewport
    // el is dom element, not jquery object
    function isElementInViewport(el) {
        var rect = el.getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) && /*or $(window).height() */
            rect.right <= (window.innerWidth || document.documentElement.clientWidth) /*or $(window).width() */
            );
    }
    var myTimeOut = false;
    window.startTimeOut = function(){
    	myTimeOut = setInterval(function(){ testIfLastLiInViewport(); }, 3000);
    }
    window.stopTimeOut = function(){
    	clearInterval(myTimeOut);
    }
    function testIfLastLiInViewport(){
    	var el = $($(".results ul")[0]).children().last()[0];
    	if( (typeof el!=="undefined") && isElementInViewport(el) ) {
            // Last li is visible, so we have to call next page manually
        	if (typeof queryobj === "object" && queryobj) {
        		$(window).trigger("scroll.ajaxload");
            }
        }
    	else{
    		window.stopTimeOut();
    	}
    }
    
    if (window.addEventListener) {
        //addEventListener('DOMContentLoaded', testIfLastLiInViewport(), false); 
        addEventListener('load', startTimeOut(), false); 
        //addEventListener('scroll', testIfLastLiInViewport(), false); 
        //addEventListener('resize', testIfLastLiInViewport(), false); 
    } else if (window.attachEvent)  {
        //attachEvent('DOMContentLoaded', testIfLastLiInViewport());
        attachEvent('load', startTimeOut());
        //attachEvent('scroll', testIfLastLiInViewport());
        //attachEvent('resize', testIfLastLiInViewport());
    }
});