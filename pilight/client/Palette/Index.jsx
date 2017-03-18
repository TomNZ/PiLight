import React, {PropTypes} from 'react';
import {
    Button,
    ButtonGroup,
    Col,
    ControlLabel,
    FormGroup,
    FormControl,
    Grid,
    InputGroup,
    Panel,
    Row,
} from 'react-bootstrap';
import {connect} from 'react-redux';
import {bindActionCreators} from 'redux';

import {setOpacity, setRadius} from '../store/palette';

import {ColorPicker} from '../Components/ColorPicker';
import {Slider} from '../Components/Slider';


class Palette extends React.Component {
    render() {
        return (
            <Grid>
                <Row>
                    <Col md={12}>
                        <h3>Base Colors</h3>
                        <p className="hidden-xs">
                            <small>
                                Specify what base colors are applied to each LED, prior to
                                transforms taking effect. Use the Solid/Smooth tool and pick
                                a color, then click on an LED.
                            </small>
                        </p>
                    </Col>
                </Row>
                <Row>
                    <Col xs={12} sm={4} md={2}>
                        <ButtonGroup>
                            <Button>Solid</Button>
                            <Button>Smooth</Button>
                        </ButtonGroup>
                    </Col>
                    <Col xs={12} sm={4} md={3}>
                        <Slider
                            label="Radius"
                            min={0}
                            max={30}
                            onChange={this.props.setRadius}
                            value={this.props.radius}
                        />
                    </Col>
                    <Col xs={12} sm={4} md={3}>
                        <Slider
                            label="Opacity"
                            min={1}
                            max={100}
                            onChange={this.props.setOpacity}
                            value={this.props.opacity}
                        />
                    </Col>
                    <Col xs={6} md={2}>
                        <ColorPicker />
                    </Col>
                    <Col xs={6} md={2}>
                        <Button>Fill</Button>
                    </Col>
                </Row>
            </Grid>
        );
    }
}

Palette.propTypes = {
    color: PropTypes.shape({
        r: PropTypes.number,
        g: PropTypes.number,
        b: PropTypes.number,
        a: PropTypes.number,
    }),
    opacity: PropTypes.number,
    radius: PropTypes.number,
};

const mapStateToProps = (state) => {
    const {palette} = state;
    return {
        color: palette.color,
        opacity: palette.opacity,
        radius: palette.radius,
    }
};

const mapDispatchToProps = (dispatch) => {
    return bindActionCreators({
        setOpacity,
        setRadius
    }, dispatch);
};

const PaletteRedux = connect(mapStateToProps, mapDispatchToProps)(Palette);

export {PaletteRedux as Palette};
