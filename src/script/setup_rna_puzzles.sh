#!/bin/bash

INPUT_DIR="docker_data/input/TestSetIII";

function setup_folders(){
  mkdir -p ${INPUT_DIR}/tmp ${INPUT_DIR}/{NATIVE,PREDS};
}
function clone_and_copy_data(){
  git clone --depth 1 https://github.com/RNA-Puzzles/standardized_dataset.git ${INPUT_DIR}/tmp;
}

function change_data_format_order(){
  folders=$(ls ${INPUT_DIR}/tmp | grep "rp" | grep -v "rp16_TBA");
  for dir in $folders; do
      name=${INPUT_DIR}/tmp/${dir};
      mkdir -p ${INPUT_DIR}/PREDS/${dir};
      native=$(ls ${name} | grep -E "solution|soluton.*\.pdb$" | grep -E '\.pdb$');
      mv ${INPUT_DIR}/tmp/${dir}/${native} ${INPUT_DIR}/tmp/${dir}/${dir}.pdb;
      cp ${INPUT_DIR}/tmp/${dir}/${dir}.pdb ${INPUT_DIR}/NATIVE/;
     mv ${INPUT_DIR}/tmp/${dir}/*.pdb ${INPUT_DIR}/PREDS/${dir}/;
  done
  rm -rf ${INPUT_DIR}/tmp;
}

setup_folders;
clone_and_copy_data;
change_data_format_order;