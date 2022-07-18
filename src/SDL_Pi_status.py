import SDL_Pi_SunControl

# config
sunControl = SDL_Pi_SunControl.SDL_Pi_SunControl(
        INA3221Address = 0x40,
        USBControlEnable = 26,
        USBControlControl = 21,
        WatchDog_Done = 13,
        WatchDog_Wake = 16
)

label = 'LIPO_Battery'
print('%s Load Voltage :\t  %3.2f V' % (label, sunControl.readChannelVoltageV(SDL_Pi_SunControl.SunControl_LIPO_BATTERY_CHANNEL)))
print('%s Current :\t\t  %3.2f mA' % (label, sunControl.readChannelCurrentmA(SDL_Pi_SunControl.SunControl_LIPO_BATTERY_CHANNEL)))
print()

label = 'Solar Cell'
print('%s Load Voltage :\t  %3.2f V' % (label, sunControl.readChannelVoltageV(SDL_Pi_SunControl.SunControl_SOLAR_CELL_CHANNEL)))
print('%s Current :\t\t  %3.2f mA' % (label, sunControl.readChannelCurrentmA(SDL_Pi_SunControl.SunControl_SOLAR_CELL_CHANNEL)))
print()

label = 'Output'
print('%s Load Voltage :\t\t  %3.2f V' % (label, sunControl.readChannelVoltageV(SDL_Pi_SunControl.SunControl_OUTPUT_CHANNEL)))
print('%s Current :\t\t  %3.2f mA' % (label, sunControl.readChannelCurrentmA(SDL_Pi_SunControl.SunControl_OUTPUT_CHANNEL)))
print()
