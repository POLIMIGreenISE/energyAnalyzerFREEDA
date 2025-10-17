serviceConnection(checkoutservice, currencyservice, 1.0036967316395136e-06, 0.0010036967316395136).
serviceConnection(checkoutservice, emailservice, 1.5336298900856789e-06, 0.0015336298900856789).
serviceConnection(checkoutservice, paymentservice, 4.222178494894573e-07, 0.0004222178494894573).
serviceConnection(checkoutservice, productcatalogservice, 6.026168169467995e-07, 0.0006026168169467995).
serviceConnection(checkoutservice, shippingservice, 1.4862172026675564e-06, 0.0014862172026675563).
serviceConnection(frontend, productcatalogservice, 3.193158733149987e-05, 0.031931587331499874).
serviceConnection(frontend, recommendationservice, 9.593180262514066e-06, 0.009593180262514066).
serviceConnection(frontend, shippingservice, 2.220275308095603e-06, 0.0022202753080956027).
serviceConnection(frontend, adservice, 4.701040297916905e-06, 0.004701040297916905).
serviceConnection(checkoutservice, cartservice, 7.824486654978678e-07, 0.0007824486654978678).
serviceConnection(frontend, cartservice, 1.0145732279670878e-05, 0.010145732279670878).
serviceConnection(frontend, checkoutservice, 1.0525099772343437e-06, 0.0010525099772343437).
serviceConnection(frontend, currencyservice, 2.126555646475965e-05, 0.021265556464759652).
serviceConnection(recommendationservice, productcatalogservice, 3.5704926921195376e-06, 0.0035704926921195377).
service(frontend, 2.832213905591043, 2832.213905591043).
service(productcatalogservice, 1.2642355941709256, 1264.2355941709257).
service(currencyservice, 1.1256232468725877, 1125.6232468725877).
service(recommendationservice, 0.7709261342488694, 770.9261342488694).
service(cartservice, 0.6987781075562003, 698.7781075562003).
service(adservice, 0.3213283533240181, 321.3283533240181).
service(checkoutservice, 0.15349569886994024, 153.49569886994024).
service(shippingservice, 0.12637485890516634, 126.37485890516633).
service(emailservice, 0.0647449549711996, 64.7449549711996).
service(paymentservice, 0.04465896334503833, 44.65896334503833).
node(france, 16).
node(spain, 88).
node(germany, 132).
node(greatbritain, 213).
node(italy, 335).
deployedTo(frontend,large,france).
deployedTo(productcatalogservice,large,greatbritain).
deployedTo(recommendationservice,large,germany).
deployedTo(checkoutservice,tiny,spain).
deployedTo(adservice,tiny,germany).
deployedTo(cartservice,tiny,greatbritain).
deployedTo(shippingservice,tiny,greatbritain).
deployedTo(currencyservice,tiny,greatbritain).
deployedTo(paymentservice,tiny,italy).
deployedTo(emailservice,tiny,italy).
highConsumptionService(frontend,large,italy,1.0).
highConsumptionService(frontend,large,greatbritain,0.6358208955223881).
highConsumptionService(frontend,large,spain,0.26268656716417915).
highConsumptionService(frontend,large,germany,0.3940298507462687).
highConsumptionService(productcatalogservice,large,italy,0.44637715805123745).
highConsumptionService(productcatalogservice,large,greatbritain,0.2838159243728764).
highConsumptionService(productcatalogservice,large,spain,0.1172572833089818).
highConsumptionService(productcatalogservice,large,germany,0.1758859249634727).
canbedelayed(adservice,tiny,7,0.4354343238874902).
