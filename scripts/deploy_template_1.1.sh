#!/bin/bash

cd ..
source /home/$USER/mosaic-5g/jox/joxenv
SERIES="xenial"
BAND="13"
REPO="cs"


if [ "$REPO" == "cs" ] ; then 
   CHARM_DIR="cs:~navid-nikaein/$SERIES"
  CONFIG_DIR="$JUJU_REPOSITORY/$SERIES"
else
  CHARM_DIR="$JUJU_REPOSITORY/$SERIES"
  CONFIG_DIR="$JUJU_REPOSITORY/$SERIES"
fi 

echo "charm dir is $CHARM_DIR"


if [ "$1" == "SLICE" ] ; then 

 juju deploy $CHARM_DIR/flexran-rtc --series=$SERIES
 juju deploy $CHARM_DIR/oai-enb oai-rcc-if4p5 --series=$SERIES --config=$CONFIG_DIR/oai-enb/config/rcc.agent.if4p5.b$BAND.yaml
 juju deploy $CHARM_DIR/oai-rru oai-rru-if4p5 --series=$SERIES --config=$CONFIG_DIR/oai-rru/config/rru.if4p5.b$BAND.yaml
 juju deploy $CHARM_DIR/oai-mme --series=$SERIES
 juju deploy $CHARM_DIR/oai-hss --series=$SERIES
 juju deploy $CHARM_DIR/oai-spgw --series=$SERIES
 juju deploy mysql --series=$SERIES


elif [ "$1" == "CRAN" ] ; then 


 juju deploy $CHARM_DIR/oai-enb oai-rcc-if4p5 --series=$SERIES --config=$CONFIG_DIR/oai-enb/config/rcc.if4p5.b$BAND.yaml
 juju deploy $CHARM_DIR/oai-rru oai-rru-if4p5 --series=$SERIES --config=$CONFIG_DIR/oai-rru/config/rru.if4p5.b$BAND.yaml
 juju deploy $CHARM_DIR/oai-hss --series=$SERIES
 juju deploy $CHARM_DIR/oai-mme --series=$SERIES
 juju deploy $CHARM_DIR/oai-spgw --series=$SERIES
 juju deploy mysql --series=$SERIES


else


 juju deploy $CHARM_DIR/oai-enb --series=$SERIES --config=$CONFIG_DIR/oai-enb/config/enb.b$BAND.yaml
 juju deploy $CHARM_DIR/oai-hss --series=$SERIES
 juju deploy $CHARM_DIR/oai-mme --series=$SERIES
 juju deploy $CHARM_DIR/oai-spgw --series=$SERIES
 juju deploy mysql --series=$SERIES

fi 

juju status
