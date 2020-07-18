process run_predictions {
    input:
        path(model)
        tuple val(index), path(shard)
    output:
        tuple val(index), path('*.png'), emit: ch_predictions
    script:
        """
        #!/usr/bin/env python

        import logging

        import tensorflow as tf

        from data_record import parse_record
        from frozen_graph import wrap_frozen_graph

        logger = tf.get_logger()
        logger.propagate = False
        logger.setLevel('INFO')

        with tf.io.gfile.GFile('${model}', "rb") as f:
            graph_def = tf.compat.v1.GraphDef()
            graph_def.ParseFromString(f.read())

        predict = wrap_frozen_graph(
            graph_def,
            inputs='ImageTensor:0',
            outputs='SemanticPredictions:0')

        dataset = (
            tf.data.TFRecordDataset('${shard}')
            .map(parse_record)
            .batch(1)
            .prefetch(1)
            .enumerate(start=1))

        size = len(list(dataset))

        for index, sample in dataset:
            filename = sample['filename'].numpy()[0].decode('utf-8')
            logger.info("Running prediction on image %s (%d/%d)" % (filename,index,size))
            raw_segmentation = predict(sample['original'])[0][:, :, None]
            output = tf.image.encode_png(tf.cast(raw_segmentation, tf.uint8))
            tf.io.write_file(filename.rsplit('.', 1)[0] + '.png',output)
        """
}