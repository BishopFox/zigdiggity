from zigdiggity.datastore.devices import Device
from zigdiggity.datastore.networks import Network
from sqlalchemy import and_

#
# While inserting data, some data may not be present, we'll go through and adjust all the data we can
#
def merge_datasource_data(datasource):

    # Check to see if we can merge records missing extended PANs
    for device in datasource.query(Device).filter_by(extended_pan_id=None).all():

        # print "Device: %s"%device
        # if it has the extended address, we need to keep the device around
        if not device.extended_address is None:
            continue

        better_device = datasource.query(Device).filter(and_(Device.channel==device.channel, Device.pan_id==device.pan_id, Device.address==device.address, Device.extended_address!=None)).first()
        # print "Better Device: %s"%better_device
        if not better_device is None:
            datasource.delete(device)
        else:
            # second we check to see if there is network mapping for the device's PAN to epan
            network = datasource.query(Network).filter_by(pan_id=device.pan_id).first()
            if not network is None:
                device.extended_pan_id = network.extended_pan_id

    print "Comparing extended addresses"

    # Check to see if we have a record for items lacking an extended address
    for device in datasource.query(Device).filter_by(extended_address=None).all():

        # print "Device: %s"%device
        # check to see if there is a device with more information
        better_device = datasource.query(Device).filter(Device.channel==device.channel and Device.pan_id==device.pan_id and Device.address==device.address and Device.extended_address!=None).first()
        # print "Better Device: %s"%better_device
        if not better_device is None:
            if better_device.extended_pan_id is None and not device.extended_pan_id is None:
                print "adding the extended pan to the better record"
                better_device.extended_pan_id = device.extended_pan_id
            datasource.delete(device)
    '''
    # Devices that have switched PAN IDs recently
    # First we'll use extended address
    for device in datasource.query(Device).filter(and_(Device.extended_address!=None, Device.pan_id!=None)).all():
        
        pan_candidates = set()
        pan_candidates.add(device.pan_id)
        for duplicate_device in datasource.query(Device).filter(and_(Device.extended_address==device.extended_address, Device.pan_id!=device.pan_id, Device.pan_id!=None)).all():
            pan_candidates.add(duplicate_device.pan_id)
  
        latest_pan = None
        latest_pan_updated = None
        for pan in pan_candidates:
            if latest_pan is None:
                network = datasource.query(Network).filter_by(pan_id=pan).first()
                if not network is None:
                    latest_pan = pan
                    latest_pan_updated = network.last_updated
            else:
                network = datasource.query(Network).filter_by(pan_id=pan).first()
                if not network is None:
                    if network.latest_updated > latest_pan_updated:
                        latest_pan = pan
                        latest_pan_updated = network.last_updated

        device.pan_id=latest_pan
    
    for device in datasource.query(Device).filter(and_(Device.extended_pan_id!=None, Device.pan_id!=None, Device.address!=None)).all():
    
        pan_candidates = set()
        pan_candidates.add(device.pan_id)
        for duplicate_device in datasource.query(Device).filter(and_(Device.extended_pan_id==device.extended_pan_id, Device.pan_id!=device.pan_id, Device.address==device.address, Device.pan_id!=None)).all():
            pan_candidates.add(duplicate_device.pan_id)
  
        latest_pan = None
        latest_pan_updated = None
        for pan in pan_candidates:
            if latest_pan is None:
                network = datasource.query(Network).filter_by(pan_id=pan).first()
                if not network is None:
                    latest_pan = pan
                    latest_pan_updated = network.last_updated
            else:
                network = datasource.query(Network).filter_by(pan_id=pan).first()
                if not network is None:
                    if network.latest_updated > latest_pan_updated:
                        latest_pan = pan
                        latest_pan_updated = network.last_updated

        device.pan_id=latest_pan
    '''

    datasource.commit()

