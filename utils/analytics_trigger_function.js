// trigger function implemented through atlas ui
// eventually i would like this to hit an endpoint

exports = async function (changeEvent) {
  // insert the _id of the document with a is_processed field so that our analytics service knows when new data is coming in
  const collection_analytics = context.services.get("mongodb-atlas").db("dragonfly").collection("event_analytics");
  try {
    await collection_analytics.insertOne({
      new_event_id: changeEvent.fullDocument._id,
      processed: false
    });
  } catch (err) {
    console.error("Failed to push update to event_analytics.", err);
  }
};