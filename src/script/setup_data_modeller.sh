#!/bin/bash

INPUT_DIR="docker_data/input/TestSetI";

function setup_dir(){
  mkdir -p ${INPUT_DIR}/{NATIVE,PREDS}
}

function download_raw_data(){
  mkdir -p ${INPUT_DIR}/tmp;
  wget -O ${INPUT_DIR}/tmp/randstr.tar.gz http://melolab.org/supmat/RNApot/Sup._Data_files/randstr.tar.gz
  tar -xzf ${INPUT_DIR}/tmp/randstr.tar.gz -C ${INPUT_DIR}/tmp;
}

function change_data_format_order(){
  dirname=${INPUT_DIR}/tmp/decoys;
  directories=$(ls ${dirname});
  for dir in ${directories}; do
    mkdir -p ${INPUT_DIR}/PREDS/${dir};
    rm ${dirname}/${dir}/*.rmsd;
    cp ${dirname}/${dir}/*.pdb ${INPUT_DIR}/PREDS/${dir};
    cp ${dirname}/${dir}/${dir}.pdb ${INPUT_DIR}/NATIVE/${dir}.pdb;
  done
  rm -rf ${INPUT_DIR}/tmp;
}

setup_dir;
download_raw_data;
change_data_format_order;
